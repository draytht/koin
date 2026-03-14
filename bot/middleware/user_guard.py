import logging
from bot.infrastructure.supabase_client import get_supabase
import asyncio

logger = logging.getLogger(__name__)


async def resolve_user_id(discord_id: str) -> str | None:
    """Returns internal user UUID if profile exists, else None."""
    supabase = get_supabase()

    def _query():
        return supabase.table("users").select("id").eq("discord_id", discord_id).maybe_single().execute()

    result = await asyncio.to_thread(_query)
    if result and result.data:
        return result.data["id"]
    return None


async def require_profile(discord_id: str) -> str:
    """Returns user UUID or raises ValueError with helpful message."""
    user_id = await resolve_user_id(discord_id)
    if not user_id:
        raise ValueError("No profile found. Run `/user create` first.")
    return user_id
