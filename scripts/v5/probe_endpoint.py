#!/usr/bin/env python3
"""Probe the LLM endpoint(s) exposed by cloud-agent secrets and report which
models each key can see — the decision input for (a) confirming the v4-source
trio (claude/gpt/deepseek class) for mutant generation and (b) choosing the
held-out MR model (must NOT be a v4 family; ranking: Gemini > Qwen > Mistral).

Reads secrets via the same adapter chains as the generation scripts:
  base_url / api_key_1 (generation arm), api_key_2 (held-out arm).
Writes nothing; prints a report. Read-only GET {base_url}/v1/models.
"""
import json
import os
import sys
import urllib.request

V4_FAMILIES = ("claude", "gpt", "deepseek")
HELDOUT_PREFERENCE = ("gemini", "qwen", "mistral", "llama", "glm", "kimi")


def probe(base_url: str, key: str, label: str) -> list[str]:
    url = base_url.rstrip("/") + "/v1/models"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
    except Exception as e:
        print(f"[{label}] probe FAILED: {e}")
        return []
    ids = sorted(m.get("id", "?") for m in data.get("data", []))
    print(f"[{label}] {len(ids)} models visible")
    v4ish = [m for m in ids if any(f in m.lower() for f in V4_FAMILIES)]
    heldout = [m for m in ids if any(f in m.lower() for f in HELDOUT_PREFERENCE)]
    print(f"  v4-family candidates (generation trio): {v4ish[:12]}")
    print(f"  held-out candidates (non-v4, pref order): {heldout[:12]}")
    return ids


def _env(*names: str) -> str | None:
    """First set value among case variants (cloud injection uppercases names)."""
    for n in names:
        for cand in (n, n.upper(), n.lower()):
            v = os.environ.get(cand)
            if v:
                return v
    return None


def main() -> int:
    base = _env("base_url", "BLTCY_BASE_URL")
    k1 = _env("api_key_1", "BLTCY_API_KEY")
    k2 = _env("api_key_2", "V5_MR_API_KEY")
    if not base or not (k1 or k2):
        print("BLOCKED: secrets not present in this VM "
              "(need base_url + api_key_1/api_key_2; injected only into NEW "
              "cloud-agent runs).")
        return 2
    if k1:
        probe(base, k1, "api_key_1 (generation arm)")
    if k2 and k2 != k1:
        probe(base, k2, "api_key_2 (held-out arm)")
    print("\nNext: set V5_MR_MODEL to a held-out candidate visible above, "
          "then run generate_v5_mutants.py / generate_v5_mrs.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
