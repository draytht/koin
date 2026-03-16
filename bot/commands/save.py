import discord
from discord.ext import commands
from bot.middleware.rate_limiter import check_rate_limit
from bot.middleware.user_guard import require_profile
from bot.services import saving_service
from bot.models.saving import SavingCreate
from bot.utils.formatters import saving_embed, error_embed
from bot.utils.validators import validate_date


class SaveCommands(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="save", description="Log a saving")
    async def save(
        self,
        ctx: discord.ApplicationContext,
        amount: discord.Option(float, "Amount saved", required=True),
        goal: discord.Option(str, "What are you saving for?", required=True),
        note: discord.Option(str, "Optional note", required=False),
        date: discord.Option(str, "Date (YYYY-MM-DD, default: today)", required=False),
    ):
        await ctx.defer(ephemeral=True)
        discord_id = str(ctx.author.id)

        if not check_rate_limit(discord_id, "save"):
            await ctx.respond(embed=error_embed("Slow down! Try again in a minute."))
            return

        try:
            user_id = await require_profile(discord_id)
            save_date = validate_date(date)

            data = SavingCreate(amount=amount, goal=goal, note=note, date=save_date)
            result = await saving_service.log_saving(user_id, data)
            embed = saving_embed(
                amount=result["amount"],
                goal=result["goal"],
                monthly_total=result["monthly_total"],
                note=result.get("note"),
                date=save_date,
            )
            await ctx.respond(embed=embed)
        except ValueError as e:
            await ctx.respond(embed=error_embed(str(e)))


def setup(bot: discord.Bot) -> SaveCommands:
    return SaveCommands(bot)
