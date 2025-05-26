import os
import asyncio
from openai import AsyncOpenAI
from pathlib import Path
from dotenv import load_dotenv

from backend._utils import LogConfig, SSEManager
from backend.service_center.agent.system_prompt_const import SYSTEM_PROMPT

logger = LogConfig.get_logger(__name__)

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
        )
    return _client


MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")


async def stream_llm(cid: str, user_msg: str, system_prompt: str | None = None, messages: list | None = None):
    """调用 OpenAI 并将增量推送到 SSE 队列 (适配 openai>=1.0)"""
    queue = SSEManager.get_queue(cid)
    if queue is None:
        logger.error(f"SSE channel {cid} not found")
        return

    # 优先使用多轮上下文
    if messages and isinstance(messages, list):
        chat_messages = messages.copy()
        # 如果没有 system 消息，插入硬编码 systemPrompt
        if not any(m.get("role") == "system" for m in chat_messages):
            chat_messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
    else:
        chat_messages = []
        chat_messages.append({"role": "system", "content": SYSTEM_PROMPT})
        chat_messages.append({"role": "user", "content": user_msg})

    try:
        client = get_client()
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=chat_messages,
            stream=True,
        )
        async for chunk in response:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                await queue.put({"event": "delta", "data": delta})
        await queue.put({"event": "end", "data": ""})
    except Exception as e:
        logger.error(f"OpenAI stream error: {e}")
        await queue.put({"event": "end", "data": ""}) 