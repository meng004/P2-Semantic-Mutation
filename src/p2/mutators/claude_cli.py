"""Subscription-auth Opus generator: shells out to `claude -p` per call.

Used as a drop-in alternative to AsyncSemaphoreClient for the generator
side of operator_runner. The reviewer side stays on the configured
OpenAI-compatible proxy (see ``llm_client.py``).

Auth comes from Claude Code's macOS keychain entry; no API key needed.
"""
import asyncio
import json
from dataclasses import dataclass

# A minimal system prompt overrides Claude Code's default coding-agent
# system prompt so the model behaves like a pure text generator.
_GENERATOR_SYSTEM = (
    "You are a precise code generator for software-testing research. "
    "Follow the user's instructions exactly. Output ONLY what the user "
    "asks for — no commentary, no markdown fences, no tool calls."
)


@dataclass
class ClaudeCLIClient:
    """Concurrency-gated wrapper around `claude -p` subprocess invocations."""
    concurrency: int = 12

    def __post_init__(self):
        self.semaphore = asyncio.Semaphore(self.concurrency)


async def claude_cli_chat(
    client: ClaudeCLIClient,
    prompt: str,
    model: str = "opus",
    retries: int = 3,
    backoff_base: float = 2.0,
    timeout_s: float = 240.0,
) -> str:
    """One headless `claude -p` invocation; returns the result string.

    On final failure returns a string starting with '# LLM_ERROR:' so the
    caller can filter without extra exception handling.
    """
    args = [
        "claude", "-p",
        "--model", model,
        "--output-format", "json",
        "--permission-mode", "bypassPermissions",
        "--no-session-persistence",
        "--disable-slash-commands",
        "--system-prompt", _GENERATOR_SYSTEM,
    ]
    async with client.semaphore:
        last_err = ""
        for attempt in range(retries):
            try:
                proc = await asyncio.create_subprocess_exec(
                    *args,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(prompt.encode("utf-8")),
                    timeout=timeout_s,
                )
                if proc.returncode != 0:
                    raise RuntimeError(
                        f"exit={proc.returncode}: {stderr.decode('utf-8', 'replace')[:200]}"
                    )
                result = json.loads(stdout.decode("utf-8"))
                if result.get("is_error"):
                    raise RuntimeError(
                        f"api_error: {result.get('result', '')[:200]}"
                    )
                content = result.get("result", "")
                if not content:
                    raise ValueError("empty result from claude CLI")
                return content
            except Exception as e:
                last_err = f"{type(e).__name__}: {str(e)[:200]}"
                if attempt < retries - 1:
                    await asyncio.sleep(backoff_base ** attempt)
        return f"# LLM_ERROR: {last_err}"
