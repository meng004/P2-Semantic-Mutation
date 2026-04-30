"""Async OpenAI-compatible client + Semaphore for high-concurrency campaigns."""
import asyncio
from dataclasses import dataclass
from openai import AsyncOpenAI


@dataclass
class AsyncSemaphoreClient:
    api_key: str
    base_url: str
    concurrency: int = 20

    def __post_init__(self):
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        self.semaphore = asyncio.Semaphore(self.concurrency)


async def async_chat_completion(
    client: AsyncSemaphoreClient,
    model: str,
    messages: list[dict],
    temperature: float,
    max_tokens: int,
    retries: int = 3,
    backoff_base: float = 1.5,
) -> str:
    """Make one chat-completion call, gated by client.semaphore.

    Retries on any exception with exponential backoff. Returns raw string content.
    On final failure, returns a string starting with "# LLM_ERROR:" so callers
    can filter without extra exception handling.
    """
    async with client.semaphore:
        last_err = ""
        for attempt in range(retries):
            try:
                resp = await client.client.chat.completions.create(
                    model=model, temperature=temperature,
                    max_tokens=max_tokens, messages=messages,
                )
                content = resp.choices[0].message.content
                if content is None:
                    raise ValueError("API returned None content")
                return content
            except Exception as e:
                last_err = f"{type(e).__name__}: {e}"
                if attempt < retries - 1:
                    await asyncio.sleep(backoff_base ** attempt)
        return f"# LLM_ERROR: {last_err}"
