import asyncio
import logging
from datetime import datetime
from bot.infrastructure.supabase_client import get_supabase
from bot.models.user import User

logger = logging.getLogger(__name__)


async def create_user(discord_id: str, username: str, currency: str = "USD", timezone: str = "UTC") -> User:
    supabase = get_supabase()

    def _check_exists():
        return supabase.table("users").select("id").eq("discord_id", discord_id).maybe_single().execute()

    existing = await asyncio.to_thread(_check_exists)
    if existing and existing.data:
        raise ValueError("You already have a profile. Use `/user update` to change settings.")

    def _insert():
        return supabase.table("users").insert({
            "discord_id": discord_id,
            "username": username,
            "currency": currency.upper(),
            "timezone": timezone,
        }).execute()

    result = await asyncio.to_thread(_insert)
    data = result.data[0]
    return User(**data)


async def get_user(discord_id: str) -> User | None:
    supabase = get_supabase()

    def _query():
        return supabase.table("users").select("*").eq("discord_id", discord_id).maybe_single().execute()

    result = await asyncio.to_thread(_query)
    if result and result.data:
        return User(**result.data)
    return None
