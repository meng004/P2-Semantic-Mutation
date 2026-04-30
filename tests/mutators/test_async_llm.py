import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from p2.mutators.async_llm import (
    AsyncSemaphoreClient, async_chat_completion,
)


def test_semaphore_limits_concurrency():
    client = AsyncSemaphoreClient(api_key="x", base_url="x", concurrency=2)
    assert client.semaphore._value == 2


@patch("p2.mutators.async_llm.AsyncOpenAI")
def test_async_chat_completion_uses_semaphore(mock_cls):
    inst = MagicMock()
    completion = AsyncMock()
    completion.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="hello"))]
    )
    inst.chat.completions.create = completion
    mock_cls.return_value = inst

    client = AsyncSemaphoreClient(api_key="x", base_url="x", concurrency=1)

    async def run():
        return await async_chat_completion(
            client=client, model="m", messages=[{"role": "user", "content": "hi"}],
            temperature=0.5, max_tokens=10,
        )

    out = asyncio.run(run())
    assert out == "hello"
    completion.assert_called_once()
