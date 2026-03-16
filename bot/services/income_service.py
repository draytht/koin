import asyncio
import logging
from datetime import date
from bot.infrastructure.supabase_client import get_supabase
from bot.models.income import IncomeCreate
from bot.utils.validators import validate_amount
from bot.utils.date_utils import start_of_month

logger = logging.getLogger(__name__)


async def log_income(user_id: str, data: IncomeCreate) -> dict:
    supabase = get_supabase()
    inc_date = data.date or date.today()
    amount = validate_amount(data.amount)

    row = {
        "user_id": user_id,
        "amount": amount,
        "source": data.source,
        "note": data.note,
        "date": inc_date.isoformat(),
    }

    def _insert():
        return supabase.table("income").insert(row).execute()

    result = await asyncio.to_thread(_insert)
    income = result.data[0]

    monthly_total = await get_monthly_income_total(user_id)
    income["monthly_income_total"] = monthly_total
    return income


async def get_monthly_income_total(user_id: str) -> float:
    supabase = get_supabase()
    month_start = start_of_month().isoformat()

    def _query():
        return (
            supabase.table("income")
            .select("amount")
            .eq("user_id", user_id)
            .gte("date", month_start)
            .execute()
        )

    result = await asyncio.to_thread(_query)
    return sum(row["amount"] for row in (result.data or []))


async def get_income_since(user_id: str, since: date) -> list[dict]:
    supabase = get_supabase()

    def _query():
        return (
            supabase.table("income")
            .select("*")
            .eq("user_id", user_id)
            .gte("date", since.isoformat())
            .order("date", desc=True)
            .execute()
        )

    result = await asyncio.to_thread(_query)
    return result.data or []


async def find_income(user_id: str, inc_date: date, source: str, amount: float | None = None) -> list[dict]:
    supabase = get_supabase()

    def _query():
        q = (
            supabase.table("income")
            .select("*")
            .eq("user_id", user_id)
            .eq("date", inc_date.isoformat())
            .eq("source", source)
        )
        if amount is not None:
            q = q.eq("amount", amount)
        return q.execute()

    result = await asyncio.to_thread(_query)
    return result.data or []


async def delete_income(user_id: str, income_id: str) -> None:
    supabase = get_supabase()

    def _delete():
        return supabase.table("income").delete().eq("user_id", user_id).eq("id", income_id).execute()

    await asyncio.to_thread(_delete)


async def update_income(user_id: str, income_id: str, updates: dict) -> dict:
    supabase = get_supabase()

    def _update():
        return supabase.table("income").update(updates).eq("user_id", user_id).eq("id", income_id).execute()

    result = await asyncio.to_thread(_update)
    if not result.data:
        raise ValueError("Income entry not found.")
    return result.data[0]
