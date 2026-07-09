"""Unified OpenAI-compatible client factory for all three LLMs."""
import os
from openai import OpenAI


def _env(key: str) -> str:
    v = os.environ.get(key, "")
    if not v:
        raise RuntimeError(f"Environment variable {key} not set — load .env first")
    return v


def generator_client() -> tuple[OpenAI, str]:
    """Claude Opus 4.6 via an OpenAI-compatible proxy.

    Configure BLTCY_BASE_URL / BLTCY_API_KEY in .env (see .env.example).
    Any OpenAI-compatible endpoint that exposes Claude Opus 4.6 works.
    """
    return (
        OpenAI(base_url=_env("BLTCY_BASE_URL"), api_key=_env("BLTCY_API_KEY")),
        "claude-opus-4-6",
    )


def reviewer1_client() -> tuple[OpenAI, str]:
    """ChatGPT 5.4 via an OpenAI-compatible proxy."""
    return (
        OpenAI(base_url=_env("BLTCY_BASE_URL"), api_key=_env("BLTCY_API_KEY")),
        "gpt-5.4",
    )


def reviewer2_client() -> tuple[OpenAI, str]:
    """DeepSeek V4 Pro via its OpenAI-compatible endpoint.

    Configure DEEPSEEK_BASE_URL / DEEPSEEK_API_KEY in .env.
    """
    return (
        OpenAI(base_url=_env("DEEPSEEK_BASE_URL"), api_key=_env("DEEPSEEK_API_KEY")),
        "deepseek-v4-pro",
    )


# Phase A: cross-source mutant generators (deepseek-chat replaces V4-Pro for
# 6x lower latency and 3x lower token cost — V4-Pro is a reasoning model
# whose reasoning_content overhead (~230 tokens/req) provides no quality gain
# for mutant generation).

def generator_claude() -> tuple[OpenAI, str]:
    """Phase A LLM-G #1: Claude Opus 4.6 (same as default generator)."""
    return generator_client()


def generator_gpt() -> tuple[OpenAI, str]:
    """Phase A LLM-G #2: GPT-5.4 via an OpenAI-compatible proxy."""
    return (
        OpenAI(base_url=_env("BLTCY_BASE_URL"), api_key=_env("BLTCY_API_KEY")),
        "gpt-5.4",
    )


def generator_deepseek() -> tuple[OpenAI, str]:
    """Phase A LLM-G #3: DeepSeek chat (NOT V4-Pro, see module note)."""
    return (
        OpenAI(base_url=_env("DEEPSEEK_BASE_URL"), api_key=_env("DEEPSEEK_API_KEY")),
        "deepseek-chat",
    )


# ══════════════════════════════════════════════════════════════════════════
# Study-4 (H2-2 cross-vendor) — four-vendor gateway layer, CONFIG-DRIVEN.
#
# All four vendors are served over ONE OpenAI-compatible gateway (BLTCY_BASE_URL
# / BLTCY_API_KEY). The model that fills each generator slot / review role is
# read from the Study-4 config (p2.config.study4, pinned by the registration);
# nothing here hardcodes a vendor into a role. Per-model quirks travel with the
# client so the campaign can apply them uniformly:
#
#   claude-fable-5   (Anthropic) — same-arm generator + blind reviewer
#   gpt-5.5          (OpenAI)    — cross slot src1 + arbiter
#   gemini-3.5-flash (Google)    — cross slot src2; NEEDS max_tokens >= 2000
#                                  (reasoning eats the budget, else empty body)
#   grok-4.1         (xAI)       — cross slot src3. The gateway SERVES this id
#                                  as grok-4.3: response.model self-reports
#                                  "grok-4.3", which the campaign records at
#                                  runtime (usage/model echo) and the config
#                                  pins as served_as. grok also emits BARE ```
#                                  fences (no python tag).
# ══════════════════════════════════════════════════════════════════════════
from p2.config import study4 as _s4  # noqa: E402


def gateway_client() -> OpenAI:
    """One OpenAI-compatible client bound to the Study-4 cross-vendor gateway."""
    base_env, key_env = _s4.gateway_env()
    return OpenAI(base_url=_env(base_env), api_key=_env(key_env))


def study4_client(model_id: str) -> tuple[OpenAI, str, dict]:
    """Return (client, model_id, quirks) for a Study-4 model over the gateway.

    ``quirks`` carries ``min_max_tokens`` (the gemini floor), ``served_as`` (the
    grok-4.1 -> grok-4.3 mapping the caller confirms against response.model),
    ``vendor`` and ``price_per_mtok`` for cost accounting.
    """
    return gateway_client(), model_id, _s4.model_quirks(model_id)


def study4_slot_factories(arm: str) -> list[tuple[str, "callable"]]:  # type: ignore[type-arg]
    """[(slot_tag, factory), ...] for an arm; factory() -> (client, model, quirks).

    slot_tag is vendor-neutral (src1/src2/src3) and identical across arms, so it
    never leaks the vendor or the arm into filenames or blinded review packets.
    """
    out = []
    for tag, model_id in _s4.arm_slots(arm):
        out.append((tag, lambda m=model_id: study4_client(m)))
    return out


def study4_role_factory(role: str) -> "callable":  # type: ignore[type-arg]
    """factory() -> (client, model, quirks) for a review role ('reviewer'|'arbiter')."""
    model_id = _s4.role_model(role)
    return lambda: study4_client(model_id)
