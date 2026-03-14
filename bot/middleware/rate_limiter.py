import time
import logging
from collections import defaultdict
from bot.config import config

logger = logging.getLogger(__name__)

# In-memory store: {(discord_id, command): [timestamp, ...]}
_call_log: dict[tuple, list[float]] = defaultdict(list)


def check_rate_limit(discord_id: str, command: str) -> bool:
    """Returns True if allowed, False if rate limited."""
    limits = config.RATE_LIMITS.get(command)
    if not limits:
        return True
    max_calls, window = limits
    now = time.monotonic()
    key = (discord_id, command)
    # Purge old entries
    _call_log[key] = [t for t in _call_log[key] if now - t < window]
    if len(_call_log[key]) >= max_calls:
        logger.warning(f"Rate limit hit: discord_id={discord_id} command={command}")
        return False
    _call_log[key].append(now)
    return True
