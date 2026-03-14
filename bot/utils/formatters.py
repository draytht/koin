import discord
from datetime import date


def currency(amount: float, symbol: str = "$") -> str:
    return f"{symbol}{amount:,.2f}"


def expense_embed(amount: float, category: str, merchant: str | None, monthly_total: float, currency_symbol: str = "$") -> discord.Embed:
    embed = discord.Embed(color=discord.Color.green())
    embed.title = "Expense Logged"
    embed.add_field(name="Amount", value=currency(amount, currency_symbol), inline=True)
    embed.add_field(name="Category", value=category.title(), inline=True)
    if merchant:
        embed.add_field(name="Merchant", value=merchant, inline=True)
    embed.set_footer(text=f"Monthly {category} total: {currency(monthly_total, currency_symbol)}")
    return embed


def income_embed(amount: float, source: str, monthly_total: float, currency_symbol: str = "$") -> discord.Embed:
    embed = discord.Embed(color=discord.Color.blue())
    embed.title = "Income Logged"
    embed.add_field(name="Amount", value=currency(amount, currency_symbol), inline=True)
    embed.add_field(name="Source", value=source.replace("_", " ").title(), inline=True)
    embed.set_footer(text=f"Monthly income total: {currency(monthly_total, currency_symbol)}")
    return embed


def debt_list_embed(debts: list[dict], currency_symbol: str = "$") -> discord.Embed:
    embed = discord.Embed(title="Your Debts", color=discord.Color.red())
    if not debts:
        embed.description = "No debts tracked. Use `/debt add` to add one."
        return embed
    total = sum(d["current_balance"] for d in debts)
    monthly_min = sum(d["minimum_payment"] for d in debts)
    for d in debts:
        pct = (d["current_balance"] / d["total_amount"] * 100) if d["total_amount"] else 0
        embed.add_field(
            name=f"{d['debt_name']} ({d['creditor']})",
            value=(
                f"Balance: {currency(d['current_balance'], currency_symbol)} / {currency(d['total_amount'], currency_symbol)} ({pct:.0f}%)\n"
                f"Rate: {d['interest_rate'] * 100:.2f}% | Min payment: {currency(d['minimum_payment'], currency_symbol)}"
            ),
            inline=False,
        )
    embed.set_footer(text=f"Total owed: {currency(total, currency_symbol)} | Monthly minimums: {currency(monthly_min, currency_symbol)}")
    return embed


def receipt_preview_embed(parsed: dict, currency_symbol: str = "$") -> discord.Embed:
    embed = discord.Embed(title="Receipt Preview — Confirm to Save", color=discord.Color.orange())
    embed.add_field(name="Merchant", value=parsed.get("merchant") or "Unknown", inline=True)
    if parsed.get("total") is not None:
        embed.add_field(name="Total", value=currency(parsed["total"], currency_symbol), inline=True)
    if parsed.get("date"):
        embed.add_field(name="Date", value=parsed["date"], inline=True)
    if parsed.get("tax") is not None:
        embed.add_field(name="Tax", value=currency(parsed["tax"], currency_symbol), inline=True)
    embed.set_footer(text="React with ✅ to save or ❌ to discard.")
    return embed


def error_embed(message: str) -> discord.Embed:
    return discord.Embed(description=f"❌ {message}", color=discord.Color.red())
