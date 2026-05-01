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


# Phase A: cross-source mutant generators (deepseek-chat replaces V4-Pro for
# 6x lower latency and 3x lower token cost — V4-Pro is a reasoning model
# whose reasoning_content overhead (~230 tokens/req) provides no quality gain
# for mutant generation).

def generator_claude() -> tuple[OpenAI, str]:
    """Phase A LLM-G #1: Claude Opus 4.6 (same as default generator)."""
    return generator_client()


def generator_gpt() -> tuple[OpenAI, str]:
    """Phase A LLM-G #2: GPT-5.4 via bltcy.ai."""
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
