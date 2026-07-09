"""Study-4 (H2-2 cross-vendor) model / role configuration loader.

The model-role mapping (which vendor fills which generator SLOT in each arm,
which model reviews, which arbitrates) is CONFIG-DRIVEN: it is read from a JSON
config that PREREGISTRATION_STUDY4 pins before the confirmatory run. Nothing in
the client or the campaign driver hardcodes a vendor into a role.

Resolution order for the config path:
  1. env ``P2_STUDY4_CONFIG`` (absolute or repo-relative path), else
  2. ``configs/study4_models.json`` at the repo root, else
  3. the baked-in ``_DEFAULT`` below (kept byte-equal to the shipped JSON so a
     missing file never silently changes the roster).

All four models are served over ONE OpenAI-compatible gateway; only the model
id and its per-model quirks differ. Quirks currently modelled:
  * ``min_max_tokens`` — a floor on ``max_tokens`` (gemini-3.5-flash needs
    >= 2000 because reasoning eats the budget);
  * ``served_as`` — the id the gateway actually serves (grok-4.1 -> grok-4.3),
    recorded at runtime from ``response.model``;
  * ``price_per_mtok`` — USD per 1e6 prompt/completion tokens, for cost
    accounting and the confirmatory-run projection.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]

# Baked default — a byte-for-byte mirror of configs/study4_models.json so that
# a missing/renamed file degrades to the SAME roster rather than crashing.
_DEFAULT: dict = {
    "version": "study4-pilot-2026-07-09-baked",
    "gateway": {"base_url_env": "BLTCY_BASE_URL", "api_key_env": "BLTCY_API_KEY"},
    "models": {
        "claude-fable-5": {"vendor": "anthropic", "min_max_tokens": 800,
                           "served_as": "claude-fable-5",
                           "price_per_mtok": {"prompt": 3.0, "completion": 15.0}},
        "gpt-5.5": {"vendor": "openai", "min_max_tokens": 800,
                    "served_as": "gpt-5.5",
                    "price_per_mtok": {"prompt": 1.25, "completion": 10.0}},
        "gemini-3.5-flash": {"vendor": "google", "min_max_tokens": 2000,
                             "served_as": "gemini-3.5-flash",
                             "price_per_mtok": {"prompt": 0.30, "completion": 2.50}},
        "grok-4.1": {"vendor": "xai", "min_max_tokens": 800,
                     "served_as": "grok-4.3",
                     "price_per_mtok": {"prompt": 3.0, "completion": 15.0}},
    },
    "arms": {
        "same": {"slots": [{"tag": "src1", "model": "claude-fable-5"},
                           {"tag": "src2", "model": "claude-fable-5"},
                           {"tag": "src3", "model": "claude-fable-5"}]},
        "cross": {"slots": [{"tag": "src1", "model": "gpt-5.5"},
                            {"tag": "src2", "model": "gemini-3.5-flash"},
                            {"tag": "src3", "model": "grok-4.1"}]},
    },
    "roles": {"reviewer": "claude-fable-5", "arbiter": "gpt-5.5"},
    "registered_k": 3,
    "confirmatory_puts": 28,
}


def config_path() -> Path | None:
    """Resolve the pinned config path, or None if only the baked default exists."""
    env = os.environ.get("P2_STUDY4_CONFIG", "").strip()
    if env:
        p = Path(env)
        return p if p.is_absolute() else (_ROOT / p)
    p = _ROOT / "configs" / "study4_models.json"
    return p if p.exists() else None


def load_study4_config() -> dict:
    """Load the Study-4 roster. Falls back to the baked default if no file."""
    p = config_path()
    if p is not None and p.exists():
        return json.loads(p.read_text())
    return _DEFAULT


def gateway_env(cfg: dict | None = None) -> tuple[str, str]:
    cfg = cfg or load_study4_config()
    g = cfg["gateway"]
    return g["base_url_env"], g["api_key_env"]


def arm_slots(arm: str, cfg: dict | None = None) -> list[tuple[str, str]]:
    """Ordered [(slot_tag, model_id), ...] for the given arm.

    Slot tags (src1/src2/src3) are vendor-NEUTRAL and identical across arms, so
    the on-disk mutant filename and the blinded review packet cannot reveal the
    arm or the vendor. In ``same`` all three slots resolve to the same model id;
    in ``cross`` they resolve to the three distinct vendors.
    """
    cfg = cfg or load_study4_config()
    if arm not in cfg["arms"]:
        raise KeyError(f"unknown Study-4 arm {arm!r}; have {list(cfg['arms'])}")
    return [(s["tag"], s["model"]) for s in cfg["arms"][arm]["slots"]]


def role_model(role: str, cfg: dict | None = None) -> str:
    cfg = cfg or load_study4_config()
    return cfg["roles"][role]


def model_quirks(model_id: str, cfg: dict | None = None) -> dict:
    cfg = cfg or load_study4_config()
    return dict(cfg["models"].get(model_id, {}))


def min_max_tokens(model_id: str, cfg: dict | None = None) -> int:
    return int(model_quirks(model_id, cfg).get("min_max_tokens", 0) or 0)


def estimate_cost_usd(model_id: str, prompt_tokens: int | None,
                      completion_tokens: int | None, cfg: dict | None = None) -> float:
    """USD cost of one call from reported usage and the config price table."""
    price = model_quirks(model_id, cfg).get("price_per_mtok", {})
    pt = float(prompt_tokens or 0)
    ct = float(completion_tokens or 0)
    return (pt / 1e6) * float(price.get("prompt", 0.0)) + \
           (ct / 1e6) * float(price.get("completion", 0.0))
