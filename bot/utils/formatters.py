import discord
from datetime import date as date_type

# ── Colour palette ────────────────────────────────────────────────────────────
COLOR_EXPENSE = discord.Color.from_rgb(239, 68, 68)    # red-500
COLOR_INCOME  = discord.Color.from_rgb(16, 185, 129)   # emerald-500
COLOR_SAVING  = discord.Color.from_rgb(245, 158, 11)   # amber-500
COLOR_DEBT    = discord.Color.from_rgb(139, 92, 246)   # violet-500
COLOR_INFO    = discord.Color.from_rgb(59, 130, 246)   # blue-500
COLOR_SUCCESS = discord.Color.from_rgb(34, 197, 94)    # green-500
COLOR_WARNING = discord.Color.from_rgb(249, 115, 22)   # orange-500
COLOR_ERROR   = discord.Color.from_rgb(239, 68, 68)    # red-500

# ── Emoji maps ────────────────────────────────────────────────────────────────
CATEGORY_EMOJI: dict[str, str] = {
    "food":          "🍔",
    "transport":     "🚗",
    "housing":       "🏠",
    "entertainment": "🎬",
    "health":        "💊",
    "shopping":      "🛍️",
    "utilities":     "⚡",
    "education":     "📚",
    "other":         "📦",
}

SOURCE_EMOJI: dict[str, str] = {
    "paycheck":    "💼",
    "freelance":   "💻",
    "gift":        "🎁",
    "investment":  "📈",
    "side_hustle": "🔥",
    "other":       "💵",
}

PAYMENT_EMOJI: dict[str, str] = {
    "cash":     "💵",
    "debit":    "💳",
    "credit":   "💳",
    "transfer": "🔄",
    "other":    "💸",
}

HEALTH_EMOJI: dict[str, str] = {
    "excellent": "🟢",
    "good":      "🟡",
    "fair":      "🟠",
    "poor":      "🔴",
}


# ── Helpers ───────────────────────────────────────────────────────────────────
def currency(amount: float, symbol: str = "$") -> str:
    return f"{symbol}{amount:,.2f}"


def progress_bar(pct: float, width: int = 12) -> str:
    """Return a text progress bar, e.g. `████████░░░░` 67%"""
    pct = max(0.0, min(100.0, pct))
    filled = round(pct / 100 * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"`{bar}` {pct:.0f}%"


def fmt_date(d) -> str:
    if isinstance(d, str):
        return d
    if isinstance(d, date_type):
        return d.strftime("%b %d, %Y")
    return str(d)


# ── Embeds ────────────────────────────────────────────────────────────────────
def expense_embed(
    amount: float,
    category: str,
    monthly_total: float,
    merchant: str | None = None,
    note: str | None = None,
    payment_method: str | None = None,
    date: date_type | None = None,
    currency_symbol: str = "$",
) -> discord.Embed:
    cat_emoji = CATEGORY_EMOJI.get(category, "📦")
    embed = discord.Embed(
        title=f"🧾  Expense Logged",
        description=f"## {currency(amount, currency_symbol)}",
        color=COLOR_EXPENSE,
    )
    embed.add_field(name="🏷️  Category",  value=f"{cat_emoji} {category.title()}",                inline=True)
    embed.add_field(name="📅  Date",       value=fmt_date(date or date_type.today()),               inline=True)
    if merchant:
        embed.add_field(name="🏪  Merchant", value=merchant, inline=True)
    if payment_method:
        pay_emoji = PAYMENT_EMOJI.get(payment_method, "💸")
        embed.add_field(name="💳  Payment", value=f"{pay_emoji} {payment_method.title()}", inline=True)
    if note:
        embed.add_field(name="📝  Note",   value=note,    inline=False)
    embed.set_footer(text=f"📊  {category.title()} this month · {currency(monthly_total, currency_symbol)}")
    return embed


def income_embed(
    amount: float,
    source: str,
    monthly_total: float,
    note: str | None = None,
    date: date_type | None = None,
    currency_symbol: str = "$",
) -> discord.Embed:
    src_emoji = SOURCE_EMOJI.get(source, "💵")
    embed = discord.Embed(
        title="💰  Income Logged",
        description=f"## +{currency(amount, currency_symbol)}",
        color=COLOR_INCOME,
    )
    embed.add_field(name="📥  Source", value=f"{src_emoji} {source.replace('_', ' ').title()}", inline=True)
    embed.add_field(name="📅  Date",   value=fmt_date(date or date_type.today()),                  inline=True)
    if note:
        embed.add_field(name="📝  Note", value=note, inline=False)
    embed.set_footer(text=f"📊  Income this month · {currency(monthly_total, currency_symbol)}")
    return embed


def saving_embed(
    amount: float,
    goal: str,
    monthly_total: float,
    note: str | None = None,
    date: date_type | None = None,
    currency_symbol: str = "$",
) -> discord.Embed:
    embed = discord.Embed(
        title="🏦  Saving Logged",
        description=f"## +{currency(amount, currency_symbol)}",
        color=COLOR_SAVING,
    )
    embed.add_field(name="🎯  Goal", value=goal.replace("_", " ").title(), inline=True)
    embed.add_field(name="📅  Date", value=fmt_date(date or date_type.today()),              inline=True)
    if note:
        embed.add_field(name="📝  Note", value=note, inline=False)
    embed.set_footer(text=f"📊  Savings this month · {currency(monthly_total, currency_symbol)}")
    return embed


def debt_list_embed(debts: list[dict], currency_symbol: str = "$") -> discord.Embed:
    embed = discord.Embed(title="📋  Your Debts", color=COLOR_DEBT)
    if not debts:
        embed.description = "No active debts tracked.\nUse `/debt add` to add one."
        return embed

    total_owed   = sum(d["current_balance"]  for d in debts)
    monthly_mins = sum(d["minimum_payment"]  for d in debts)

    for d in debts:
        pct = (d["current_balance"] / d["total_amount"] * 100) if d["total_amount"] else 0
        bar = progress_bar(pct)
        due = f"\n📅  Due: {d['due_date']}" if d.get("due_date") else ""
        embed.add_field(
            name=f"🔴  {d['debt_name']}  ·  {d['creditor']}",
            value=(
                f"{bar}\n"
                f"**Balance:** {currency(d['current_balance'], currency_symbol)} / {currency(d['total_amount'], currency_symbol)}\n"
                f"**Rate:** {d['interest_rate'] * 100:.2f}% APR  ·  **Min:** {currency(d['minimum_payment'], currency_symbol)}/mo"
                f"{due}"
            ),
            inline=False,
        )

    embed.set_footer(
        text=f"💸  Total owed · {currency(total_owed, currency_symbol)}   |   🔄  Monthly minimums · {currency(monthly_mins, currency_symbol)}"
    )
    return embed


def debt_added_embed(result: dict, currency_symbol: str = "$") -> discord.Embed:
    embed = discord.Embed(
        title="➕  Debt Added",
        description=f"**{result['debt_name']}** has been added to your tracker.",
        color=COLOR_DEBT,
    )
    embed.add_field(name="🏦  Creditor",     value=result["creditor"],                                         inline=True)
    embed.add_field(name="💰  Total Amount", value=currency(result["total_amount"], currency_symbol),          inline=True)
    embed.add_field(name="📈  APR",          value=f"{result['interest_rate'] * 100:.2f}%",                    inline=True)
    embed.add_field(name="🔄  Min Payment",  value=f"{currency(result['minimum_payment'], currency_symbol)}/mo", inline=True)
    if result.get("due_date"):
        embed.add_field(name="📅  Due Date", value=fmt_date(result["due_date"]), inline=True)
    if result.get("note"):
        embed.add_field(name="📝  Note",     value=result["note"],               inline=False)
    return embed


def debt_updated_embed(debt_name: str, result: dict, currency_symbol: str = "$") -> discord.Embed:
    pct = (result["current_balance"] / result["total_amount"] * 100) if result["total_amount"] else 0
    embed = discord.Embed(
        title=f"✏️  Debt Updated",
        description=f"**{debt_name}** — {progress_bar(pct)}",
        color=COLOR_WARNING,
    )
    embed.add_field(name="💰  Total Amount",    value=currency(result["total_amount"], currency_symbol),          inline=True)
    embed.add_field(name="🏦  Current Balance", value=currency(result["current_balance"], currency_symbol),       inline=True)
    embed.add_field(name="📈  APR",             value=f"{result['interest_rate'] * 100:.2f}%",                    inline=True)
    embed.add_field(name="🔄  Min Payment",     value=f"{currency(result['minimum_payment'], currency_symbol)}/mo", inline=True)
    return embed


def debt_deleted_embed(debt_name: str) -> discord.Embed:
    return discord.Embed(
        title="🗑️  Debt Removed",
        description=f"**{debt_name}** has been deleted from your records.",
        color=COLOR_WARNING,
    )


def income_deleted_embed(entry: dict, currency_symbol: str = "$") -> discord.Embed:
    src_emoji = SOURCE_EMOJI.get(entry["source"], "💵")
    return discord.Embed(
        title="🗑️  Income Entry Removed",
        description=(
            f"{src_emoji} **{entry['source'].replace('_', ' ').title()}**\n"
            f"{currency(entry['amount'], currency_symbol)}  ·  {fmt_date(entry['date'])}"
        ),
        color=COLOR_WARNING,
    )


def income_updated_embed(result: dict, currency_symbol: str = "$") -> discord.Embed:
    src_emoji = SOURCE_EMOJI.get(result["source"], "💵")
    embed = discord.Embed(
        title="✏️  Income Entry Updated",
        color=COLOR_INFO,
    )
    embed.add_field(name="💰  Amount", value=currency(result["amount"], currency_symbol),                              inline=True)
    embed.add_field(name="📥  Source", value=f"{src_emoji} {result['source'].replace('_', ' ').title()}", inline=True)
    embed.add_field(name="📅  Date",   value=fmt_date(result["date"]),                                    inline=True)
    if result.get("note"):
        embed.add_field(name="📝  Note", value=result["note"], inline=False)
    return embed


def receipt_preview_embed(parsed: dict, currency_symbol: str = "$") -> discord.Embed:
    embed = discord.Embed(
        title="🧾  Receipt Preview",
        description="Review the extracted details below, then confirm to save.",
        color=COLOR_WARNING,
    )
    embed.add_field(name="🏪  Merchant", value=parsed.get("merchant") or "Unknown", inline=True)
    if parsed.get("total") is not None:
        embed.add_field(name="💰  Total", value=currency(parsed["total"], currency_symbol), inline=True)
    if parsed.get("date"):
        embed.add_field(name="📅  Date",  value=parsed["date"],                             inline=True)
    if parsed.get("tax") is not None:
        embed.add_field(name="🧾  Tax",   value=currency(parsed["tax"], currency_symbol),  inline=True)
    embed.set_footer(text="React with ✅ to save  ·  ❌ to discard")
    return embed


def user_created_embed(username: str, currency_code: str, timezone: str) -> discord.Embed:
    embed = discord.Embed(
        title="✅  Profile Created",
        description=f"Welcome to **Koin**, {username}!\nYour personal finance OS is ready.",
        color=COLOR_SUCCESS,
    )
    embed.add_field(name="💱  Currency", value=currency_code, inline=True)
    embed.add_field(name="🌍  Timezone", value=timezone,      inline=True)
    embed.set_footer(text="Run /help to see all available commands.")
    return embed


def user_profile_embed(user, avatar_url: str | None = None) -> discord.Embed:
    health_emoji = HEALTH_EMOJI.get(str(user.financial_health).lower(), "⚪")
    net = user.net_worth
    net_str = f"+{currency(net, user.currency)}" if net >= 0 else f"-{currency(abs(net), user.currency)}"
    net_color = COLOR_INCOME if net >= 0 else COLOR_EXPENSE

    embed = discord.Embed(
        title=f"👤  {user.username}'s Profile",
        color=net_color,
    )
    if avatar_url:
        embed.set_thumbnail(url=avatar_url)

    embed.add_field(name="💱  Currency",      value=user.currency,                                        inline=True)
    embed.add_field(name="🌍  Timezone",      value=user.timezone,                                        inline=True)
    embed.add_field(name="\u200b",            value="\u200b",                                             inline=True)

    embed.add_field(name="📥  Total Income",   value=currency(user.total_income,   user.currency),       inline=True)
    embed.add_field(name="📤  Total Expenses", value=currency(user.total_expenses, user.currency),       inline=True)
    embed.add_field(name="💹  Net Worth",      value=net_str,                                            inline=True)

    embed.add_field(name="🏦  Total Savings",  value=currency(user.total_savings, user.currency),       inline=True)
    embed.add_field(name="🔴  Total Debts",    value=currency(user.total_debts,   user.currency),       inline=True)
    embed.add_field(name="📊  Monthly Budget", value=currency(user.monthly_budget, user.currency),      inline=True)

    embed.add_field(
        name=f"{health_emoji}  Financial Health",
        value=str(user.financial_health).title() if user.financial_health else "—",
        inline=False,
    )
    if user.ai_insights:
        embed.add_field(name="🤖  AI Insights", value=user.ai_insights, inline=False)

    embed.set_footer(text=f"Member since {user.created_at.strftime('%b %d, %Y')}")
    return embed


def ai_embed(title: str, emoji: str, response: str, footer: str, color: discord.Color) -> discord.Embed:
    embed = discord.Embed(
        title=f"{emoji}  {title}",
        description=response,
        color=color,
    )
    embed.set_footer(text=footer)
    return embed


def error_embed(message: str) -> discord.Embed:
    return discord.Embed(
        description=f"❌  {message}",
        color=COLOR_ERROR,
    )
