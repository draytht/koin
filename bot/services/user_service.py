import asyncio
import logging
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


async def get_user_profile(discord_id: str) -> User | None:
    supabase = get_supabase()

    def _query():
        return supabase.table("users").select("*").eq("discord_id", discord_id).maybe_single().execute()

    result = await asyncio.to_thread(_query)
    if not result or not result.data:
        return None

    user = User(**result.data)
    user_id = str(user.id)

    def _income():
        return supabase.table("income").select("amount").eq("user_id", user_id).execute()

    def _expenses():
        return supabase.table("expenses").select("amount").eq("user_id", user_id).execute()

    def _debts():
        return supabase.table("debts").select("current_balance").eq("user_id", user_id).eq("is_paid_off", False).execute()

    def _savings():
        return supabase.table("savings").select("amount").eq("user_id", user_id).execute()

    def _ai_insights():
        return (
            supabase.table("ai_reports")
            .select("response_text")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

    income_res, expense_res, debt_res, saving_res, ai_res = await asyncio.gather(
        asyncio.to_thread(_income),
        asyncio.to_thread(_expenses),
        asyncio.to_thread(_debts),
        asyncio.to_thread(_savings),
        asyncio.to_thread(_ai_insights),
    )

    user.total_income = sum(r["amount"] for r in (income_res.data or []))
    user.total_expenses = sum(r["amount"] for r in (expense_res.data or []))
    user.total_debts = sum(r["current_balance"] for r in (debt_res.data or []))
    user.total_savings = sum(r["amount"] for r in (saving_res.data or []))
    user.net_worth = user.total_income - user.total_expenses - user.total_debts + user.total_savings
    user.monthly_budget = user.total_income - user.total_expenses

    if user.total_income > 0:
        savings_rate = user.total_savings / user.total_income
        debt_ratio = user.total_debts / user.total_income
        if savings_rate >= 0.2 and debt_ratio < 0.3:
            user.financial_health = "Excellent"
        elif savings_rate >= 0.1 and debt_ratio < 0.5:
            user.financial_health = "Good"
        elif savings_rate >= 0.05:
            user.financial_health = "Fair"
        else:
            user.financial_health = "Needs Attention"
    else:
        user.financial_health = "No data yet"

    if ai_res.data:
        full_text = ai_res.data[0]["response_text"]
        user.ai_insights = full_text[:200] + "..." if len(full_text) > 200 else full_text

    return user
