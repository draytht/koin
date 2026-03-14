import asyncio
import logging
from datetime import date
from bot.infrastructure.supabase_client import get_supabase
from bot.models.expense import ExpenseCreate, Expense
from bot.utils.validators import validate_amount, validate_date
from bot.utils.date_utils import start_of_month

logger = logging.getLogger(__name__)


async def log_expense(user_id: str, data: ExpenseCreate) -> dict:
    supabase = get_supabase()
    exp_date = data.date or date.today()
    amount = validate_amount(data.amount)

    row = {
        "user_id": user_id,
        "amount": amount,
        "category": data.category,
        "merchant": data.merchant,
        "note": data.note,
        "payment_method": data.payment_method,
        "date": exp_date.isoformat(),
        "recurring": data.recurring,
    }

    def _insert():
        return supabase.table("expenses").insert(row).execute()

    result = await asyncio.to_thread(_insert)
    expense = result.data[0]

    # Fetch monthly total for this category
    monthly_total = await get_monthly_category_total(user_id, data.category)
    expense["monthly_category_total"] = monthly_total
    return expense


async def get_monthly_category_total(user_id: str, category: str) -> float:
    supabase = get_supabase()
    month_start = start_of_month().isoformat()

    def _query():
        return (
            supabase.table("expenses")
            .select("amount")
            .eq("user_id", user_id)
            .eq("category", category)
            .gte("date", month_start)
            .execute()
        )

    result = await asyncio.to_thread(_query)
    return sum(row["amount"] for row in (result.data or []))


async def get_expenses_since(user_id: str, since: date) -> list[dict]:
    supabase = get_supabase()

    def _query():
        return (
            supabase.table("expenses")
            .select("*")
            .eq("user_id", user_id)
            .gte("date", since.isoformat())
            .order("date", desc=True)
            .execute()
        )

    result = await asyncio.to_thread(_query)
    return result.data or []
