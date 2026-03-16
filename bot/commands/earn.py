import logging
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)
from bot.middleware.rate_limiter import check_rate_limit
from bot.middleware.user_guard import require_profile
from bot.services import income_service
from bot.models.income import IncomeCreate
from bot.utils.formatters import income_embed, error_embed
from bot.utils.validators import INCOME_SOURCES


class EarnCommands(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="earn", description="Log income")
    async def earn(
        self,
        ctx: discord.ApplicationContext,
        amount: discord.Option(float, "Amount earned", required=True),
        source: discord.Option(str, "Income source", required=True, choices=INCOME_SOURCES),
        note: discord.Option(str, "Optional note", required=False),
        date: discord.Option(str, "Date (MM-DD-YY, default: today)", required=False),
    ):
        await ctx.defer(ephemeral=True)
        discord_id = str(ctx.author.id)

        if not check_rate_limit(discord_id, "earn"):
            await ctx.followup.send(embed=error_embed("Too many requests. Try again in a minute."), ephemeral=True)
            return

        try:
            user_id = await require_profile(discord_id)
            from bot.utils.validators import validate_date
            inc_date = validate_date(date)

            data = IncomeCreate(amount=amount, source=source, note=note, date=inc_date)
            result = await income_service.log_income(user_id, data)
            embed = income_embed(
                amount=result["amount"],
                source=result["source"],
                monthly_total=result["monthly_income_total"],
            )
            embed.add_field(name="Date", value=inc_date.strftime("%m-%d-%y"), inline=True)
            await ctx.followup.send(embed=embed, ephemeral=True)
        except ValueError as e:
            await ctx.followup.send(embed=error_embed(str(e)), ephemeral=True)
        except Exception as e:
            logger.error(f"Earn command failed: {e}", exc_info=True)
            await ctx.followup.send(embed=error_embed("Something went wrong. Please try again."), ephemeral=True)


def setup(bot: discord.Bot) -> EarnCommands:
    return EarnCommands(bot)
