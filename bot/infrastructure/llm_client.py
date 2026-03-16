import logging
import anthropic
from bot.config import config

logger = logging.getLogger(__name__)

_client: anthropic.AsyncAnthropic | None = None


def get_llm_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)
    return _client


async def chat_completion(system_prompt: str, user_prompt: str, temperature: float = 0.4) -> str:
    client = get_llm_client()
    try:
        response = await client.messages.create(
            model=config.ANTHROPIC_MODEL,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=900,
        )
        return response.content[0].text if response.content else ""
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise
