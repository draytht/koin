import discord
from discord.ext import commands
from bot.middleware.rate_limiter import check_rate_limit
from bot.middleware.user_guard import require_profile
from bot.services import expense_service
from bot.models.expense import ExpenseCreate
from bot.utils.formatters import expense_embed, error_embed
from bot.utils.validators import EXPENSE_CATEGORIES, PAYMENT_METHODS


class SpendCommands(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="spend", description="Log an expense")
    async def spend(
        self,
        ctx: discord.ApplicationContext,
        amount: discord.Option(float, "Amount spent", required=True),
        category: discord.Option(str, "Category", required=True, choices=EXPENSE_CATEGORIES),
        merchant: discord.Option(str, "Merchant/store name", required=False),
        note: discord.Option(str, "Optional note", required=False),
        payment_method: discord.Option(str, "Payment method", required=False, choices=PAYMENT_METHODS),
        date: discord.Option(str, "Date (YYYY-MM-DD, default: today)", required=False),
        recurring: discord.Option(bool, "Is this a recurring expense?", required=False, default=False),
    ):
        await ctx.defer(ephemeral=True)
        discord_id = str(ctx.author.id)

        if not check_rate_limit(discord_id, "spend"):
            await ctx.respond(embed=error_embed("Slow down! You're logging too fast. Try again in a minute."))
            return

        try:
            user_id = await require_profile(discord_id)
            from bot.utils.validators import validate_date
            exp_date = validate_date(date)

            data = ExpenseCreate(
                amount=amount,
                category=category,
                merchant=merchant,
                note=note,
                payment_method=payment_method,
                date=exp_date,
                recurring=recurring,
            )
            result = await expense_service.log_expense(user_id, data)
            embed = expense_embed(
                amount=result["amount"],
                category=result["category"],
                monthly_total=result["monthly_category_total"],
                merchant=result.get("merchant"),
                note=result.get("note"),
                payment_method=result.get("payment_method"),
                date=exp_date,
            )
            await ctx.respond(embed=embed)
        except ValueError as e:
            await ctx.respond(embed=error_embed(str(e)))


def setup(bot: discord.Bot) -> SpendCommands:
    return SpendCommands(bot)
