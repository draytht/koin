import asyncio
import logging
from bot.infrastructure.supabase_client import get_supabase
from bot.models.debt import DebtCreate

logger = logging.getLogger(__name__)


async def add_debt(user_id: str, data: DebtCreate) -> dict:
    supabase = get_supabase()

    row = {
        "user_id": user_id,
        "debt_name": data.debt_name,
        "creditor": data.creditor,
        "total_amount": data.total_amount,
        "current_balance": data.total_amount,
        "interest_rate": data.interest_rate / 100,  # store as decimal
        "minimum_payment": data.minimum_payment,
        "due_date": data.due_date.isoformat() if data.due_date else None,
        "note": data.note,
    }

    def _insert():
        return supabase.table("debts").insert(row).execute()

    try:
        result = await asyncio.to_thread(_insert)
        return result.data[0]
    except Exception as e:
        if "unique" in str(e).lower():
            raise ValueError(f"A debt named '{data.debt_name}' already exists. Use `/debt update` to modify it.")
        raise


async def update_debt(user_id: str, debt_name: str, updates: dict) -> dict:
    supabase = get_supabase()

    if "interest_rate" in updates:
        updates["interest_rate"] = updates["interest_rate"] / 100

    def _update():
        return (
            supabase.table("debts")
            .update(updates)
            .eq("user_id", user_id)
            .eq("debt_name", debt_name)
            .execute()
        )

    result = await asyncio.to_thread(_update)
    if not result.data:
        raise ValueError(f"No debt named '{debt_name}' found.")
    return result.data[0]


async def list_debts(user_id: str) -> list[dict]:
    supabase = get_supabase()

    def _query():
        return (
            supabase.table("debts")
            .select("*")
            .eq("user_id", user_id)
            .eq("is_paid_off", False)
            .order("interest_rate", desc=True)
            .execute()
        )

    result = await asyncio.to_thread(_query)
    return result.data or []


async def delete_debt(user_id: str, debt_name: str) -> None:
    supabase = get_supabase()

    def _delete():
        return supabase.table("debts").delete().eq("user_id", user_id).eq("debt_name", debt_name).execute()

    result = await asyncio.to_thread(_delete)
    if not result.data:
        raise ValueError(f"No debt named '{debt_name}' found.")


async def get_all_debts(user_id: str) -> list[dict]:
    """All debts including paid off, for AI analysis."""
    supabase = get_supabase()

    def _query():
        return (
            supabase.table("debts")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )

    result = await asyncio.to_thread(_query)
    return result.data or []
