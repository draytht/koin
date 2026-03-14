import asyncio
import logging
from io import BytesIO
from datetime import date
from bot.services.expense_service import get_expenses_since
from bot.services.income_service import get_income_since
from bot.utils.date_utils import days_ago

logger = logging.getLogger(__name__)


def _render_category_pie(expenses: list[dict]) -> bytes:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    by_category: dict[str, float] = {}
    for e in expenses:
        by_category[e["category"]] = by_category.get(e["category"], 0) + e["amount"]

    if not by_category:
        raise ValueError("No expense data to chart.")

    labels = [k.title() for k in by_category]
    values = list(by_category.values())

    fig, ax = plt.subplots(figsize=(7, 7), facecolor="#2b2d31")
    ax.set_facecolor("#2b2d31")
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, autopct="%1.1f%%",
        colors=plt.cm.Set3.colors, startangle=140,
        textprops={"color": "white"}
    )
    for at in autotexts:
        at.set_color("white")
    ax.set_title("Spending by Category", color="white", pad=20)

    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def _render_income_vs_expenses(expenses: list[dict], incomes: list[dict]) -> bytes:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from collections import defaultdict

    monthly_exp: dict[str, float] = defaultdict(float)
    monthly_inc: dict[str, float] = defaultdict(float)

    for e in expenses:
        key = e["date"][:7]  # YYYY-MM
        monthly_exp[key] += e["amount"]
    for i in incomes:
        key = i["date"][:7]
        monthly_inc[key] += i["amount"]

    all_months = sorted(set(list(monthly_exp.keys()) + list(monthly_inc.keys())))
    if not all_months:
        raise ValueError("No data to chart.")

    inc_vals = [monthly_inc.get(m, 0) for m in all_months]
    exp_vals = [monthly_exp.get(m, 0) for m in all_months]
    x = range(len(all_months))

    fig, ax = plt.subplots(figsize=(9, 5), facecolor="#2b2d31")
    ax.set_facecolor("#2b2d31")
    ax.bar([i - 0.2 for i in x], inc_vals, width=0.4, label="Income", color="#57f287", alpha=0.9)
    ax.bar([i + 0.2 for i in x], exp_vals, width=0.4, label="Expenses", color="#ed4245", alpha=0.9)
    ax.set_xticks(list(x))
    ax.set_xticklabels(all_months, rotation=30, ha="right", color="white")
    ax.tick_params(axis="y", colors="white")
    ax.set_title("Income vs Expenses", color="white", pad=15)
    ax.legend(facecolor="#2b2d31", labelcolor="white")
    ax.spines["bottom"].set_color("#555")
    ax.spines["left"].set_color("#555")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf.read()


async def generate_category_chart(user_id: str, days: int = 30) -> bytes:
    expenses = await get_expenses_since(user_id, days_ago(days))
    return await asyncio.to_thread(_render_category_pie, expenses)


async def generate_income_vs_expenses_chart(user_id: str, days: int = 90) -> bytes:
    expenses = await get_expenses_since(user_id, days_ago(days))
    incomes = await get_income_since(user_id, days_ago(days))
    return await asyncio.to_thread(_render_income_vs_expenses, expenses, incomes)
