import logging
from openai import AsyncOpenAI
from bot.config import config

logger = logging.getLogger(__name__)

_client: AsyncOpenAI | None = None


def get_llm_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
    return _client


async def chat_completion(system_prompt: str, user_prompt: str, temperature: float = 0.4) -> str:
    client = get_llm_client()
    try:
        response = await client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=900,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise
