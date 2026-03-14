import logging
from datetime import date
from bot.infrastructure.llm_client import chat_completion
from bot.infrastructure.supabase_client import get_supabase
from bot.services.expense_service import get_expenses_since
from bot.services.income_service import get_income_since
from bot.services.debt_service import list_debts
from bot.utils.date_utils import days_ago
import asyncio

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are a precise personal finance advisor analyzing real transaction data
provided to you. You do not make up numbers or invent scenarios. You only analyze the data given.
You give specific, actionable advice. You never give generic tips like "try to spend less".
Every recommendation must reference a specific number or category from the data.
You flag financial risks clearly. You are honest even when the financial picture is bad.
Response format is always:
**Financial Diagnosis**
[one paragraph]

**Problem Areas**
[bulleted list with specific numbers]

**Specific Suggestions**
[numbered list of concrete actions]

**Warnings**
[urgent flags, or "None" if healthy]"""


async def build_context(user_id: str, days: int = 30) -> dict:
    since = days_ago(days)
    expenses = await get_expenses_since(user_id, since)
    incomes = await get_income_since(user_id, since)
    debts = await list_debts(user_id)

    income_total = sum(i["amount"] for i in incomes)
    expense_total = sum(e["amount"] for e in expenses)

    by_category: dict[str, float] = {}
    for e in expenses:
        by_category[e["category"]] = by_category.get(e["category"], 0) + e["amount"]

    by_source: dict[str, float] = {}
    for i in incomes:
        by_source[i["source"]] = by_source.get(i["source"], 0) + i["amount"]

    # Top 5 merchants
    merchant_totals: dict[str, float] = {}
    for e in expenses:
        if e.get("merchant"):
            merchant_totals[e["merchant"]] = merchant_totals.get(e["merchant"], 0) + e["amount"]
    top_merchants = sorted(merchant_totals.items(), key=lambda x: x[1], reverse=True)[:5]

    recurring_total = sum(e["amount"] for e in expenses if e.get("recurring"))
    debt_total = sum(d["current_balance"] for d in debts)
    monthly_minimums = sum(d["minimum_payment"] for d in debts)

    highest_rate_debt = max(debts, key=lambda d: d["interest_rate"], default=None)

    savings_rate = (income_total - expense_total) / income_total if income_total > 0 else 0

    return {
        "period_days": days,
        "income_total": income_total,
        "expense_total": expense_total,
        "net_cashflow": income_total - expense_total,
        "savings_rate": savings_rate,
        "by_category": by_category,
        "by_source": by_source,
        "top_merchants": top_merchants,
        "recurring_total": recurring_total,
        "debt_total": debt_total,
        "monthly_minimums": monthly_minimums,
        "highest_rate_debt": highest_rate_debt,
        "debts": debts,
    }


def _format_context_prompt(ctx: dict, request_type: str) -> str:
    category_lines = "\n".join(f"  {k}: ${v:,.2f}" for k, v in ctx["by_category"].items())
    source_lines = "\n".join(f"  {k}: ${v:,.2f}" for k, v in ctx["by_source"].items())
    merchant_lines = "\n".join(f"  {m}: ${v:,.2f}" for m, v in ctx["top_merchants"])
    debt_info = ""
    if ctx["debts"]:
        debt_info = f"""
DEBTS:
  Total balance owed: ${ctx['debt_total']:,.2f}
  Monthly minimums: ${ctx['monthly_minimums']:,.2f}"""
        if ctx["highest_rate_debt"]:
            d = ctx["highest_rate_debt"]
            debt_info += f"\n  Highest rate: {d['debt_name']} at {d['interest_rate']*100:.2f}% APR"

    return f"""Analyze the following financial data for the last {ctx['period_days']} days:

INCOME: ${ctx['income_total']:,.2f} total
  By source:
{source_lines or '  (none)'}

EXPENSES: ${ctx['expense_total']:,.2f} total
  By category:
{category_lines or '  (none)'}
  Top merchants:
{merchant_lines or '  (none)'}
  Recurring expenses: ${ctx['recurring_total']:,.2f}
{debt_info}

Net cashflow: ${ctx['net_cashflow']:,.2f}
Savings rate: {ctx['savings_rate']:.1%}

User request: {request_type}"""


async def analyze(user_id: str, report_type: str = "full analysis", days: int = 30) -> str:
    ctx = await build_context(user_id, days)

    if ctx["income_total"] == 0 and ctx["expense_total"] == 0:
        return "Not enough data to analyze. Log some income with `/earn` and expenses with `/spend` first."

    prompt = _format_context_prompt(ctx, report_type)
    response = await chat_completion(_SYSTEM_PROMPT, prompt)

    # Save report
    await _save_report(user_id, report_type, ctx, response)
    return response


async def _save_report(user_id: str, report_type: str, ctx: dict, response: str):
    from bot.infrastructure.supabase_client import get_supabase
    supabase = get_supabase()

    def _insert():
        return supabase.table("ai_reports").insert({
            "user_id": user_id,
            "report_type": report_type,
            "input_summary": {
                "income_total": ctx["income_total"],
                "expense_total": ctx["expense_total"],
                "net_cashflow": ctx["net_cashflow"],
                "period_days": ctx["period_days"],
            },
            "response_text": response,
        }).execute()

    try:
        await asyncio.to_thread(_insert)
    except Exception as e:
        logger.warning(f"Failed to save AI report: {e}")
