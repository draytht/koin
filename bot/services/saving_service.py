import asyncio
import logging
from datetime import date
from bot.infrastructure.supabase_client import get_supabase
from bot.models.saving import SavingCreate
from bot.utils.validators import validate_amount
from bot.utils.date_utils import start_of_month

logger = logging.getLogger(__name__)


async def log_saving(user_id: str, data: SavingCreate) -> dict:
    supabase = get_supabase()
    save_date = data.date or date.today()
    amount = validate_amount(data.amount)

    row = {
        "user_id": user_id,
        "amount": amount,
        "goal": data.goal,
        "note": data.note,
        "date": save_date.isoformat(),
    }

    def _insert():
        return supabase.table("savings").insert(row).execute()

    result = await asyncio.to_thread(_insert)
    saving = result.data[0]

    monthly_total = await get_monthly_savings_total(user_id)
    saving["monthly_total"] = monthly_total
    return saving


async def get_monthly_savings_total(user_id: str) -> float:
    supabase = get_supabase()
    month_start = start_of_month().isoformat()

    def _query():
        return (
            supabase.table("savings")
            .select("amount")
            .eq("user_id", user_id)
            .gte("date", month_start)
            .execute()
        )

    result = await asyncio.to_thread(_query)
    return sum(row["amount"] for row in (result.data or []))


async def list_savings(user_id: str, limit: int = 10) -> list[dict]:
    supabase = get_supabase()

    def _query():
        return (
            supabase.table("savings")
            .select("*")
            .eq("user_id", user_id)
            .order("date", desc=True)
            .limit(limit)
            .execute()
        )

    result = await asyncio.to_thread(_query)
    return result.data or []


async def find_saving(user_id: str, save_date: date, goal: str, amount: float | None = None) -> list[dict]:
    supabase = get_supabase()

    def _query():
        q = (
            supabase.table("savings")
            .select("*")
            .eq("user_id", user_id)
            .eq("date", save_date.isoformat())
            .eq("goal", goal)
        )
        if amount is not None:
            q = q.eq("amount", amount)
        return q.execute()

    result = await asyncio.to_thread(_query)
    return result.data or []


async def delete_saving(user_id: str, saving_id: str) -> None:
    supabase = get_supabase()

    def _delete():
        return supabase.table("savings").delete().eq("user_id", user_id).eq("id", saving_id).execute()

    await asyncio.to_thread(_delete)


async def update_saving(user_id: str, saving_id: str, updates: dict) -> dict:
    supabase = get_supabase()

    def _update():
        return supabase.table("savings").update(updates).eq("user_id", user_id).eq("id", saving_id).execute()

    result = await asyncio.to_thread(_update)
    if not result.data:
        raise ValueError("Saving entry not found.")
    return result.data[0]
