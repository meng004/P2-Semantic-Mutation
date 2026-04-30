"""Unified OpenAI-compatible client factory for all three LLMs."""
import os
from openai import OpenAI


def _env(key: str) -> str:
    v = os.environ.get(key, "")
    if not v:
        raise RuntimeError(f"Environment variable {key} not set — load .env first")
    return v


def generator_client() -> tuple[OpenAI, str]:
    """Claude Opus 4.6 via bltcy.ai proxy."""
    return (
        OpenAI(base_url=_env("BLTCY_BASE_URL"), api_key=_env("BLTCY_API_KEY")),
        "claude-opus-4-6",
    )


def reviewer1_client() -> tuple[OpenAI, str]:
    """ChatGPT 5.4 via bltcy.ai proxy."""
    return (
        OpenAI(base_url=_env("BLTCY_BASE_URL"), api_key=_env("BLTCY_API_KEY")),
        "gpt-5.4",
    )


def reviewer2_client() -> tuple[OpenAI, str]:
    """DeepSeek V4 Pro via deepseek.com OpenAI-compatible endpoint."""
    return (
        OpenAI(base_url=_env("DEEPSEEK_BASE_URL"), api_key=_env("DEEPSEEK_API_KEY")),
        "deepseek-v4-pro",
    )
