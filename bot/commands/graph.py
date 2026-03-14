import discord
from discord.ext import commands
from io import BytesIO
from bot.middleware.rate_limiter import check_rate_limit
from bot.middleware.user_guard import require_profile
from bot.services import graph_service
from bot.utils.formatters import error_embed
import logging

logger = logging.getLogger(__name__)


class GraphCommands(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    graph_group = discord.SlashCommandGroup("graph", "Generate financial charts")

    @graph_group.command(name="category_breakdown", description="Spending by category (last 30 days)")
    async def graph_category(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=True)
        discord_id = str(ctx.author.id)

        if not check_rate_limit(discord_id, "graph"):
            await ctx.respond(embed=error_embed("Too many chart requests. Wait a minute."))
            return

        try:
            user_id = await require_profile(discord_id)
            image_bytes = await graph_service.generate_category_chart(user_id)
            file = discord.File(BytesIO(image_bytes), filename="category_breakdown.png")
            await ctx.respond(file=file, ephemeral=True)
        except ValueError as e:
            await ctx.respond(embed=error_embed(str(e)))
        except Exception as e:
            logger.error(f"Graph category failed: {e}", exc_info=True)
            await ctx.respond(embed=error_embed("Failed to generate chart."))

    @graph_group.command(name="income_vs_expenses", description="Income vs expenses by month (last 90 days)")
    async def graph_income_vs_expenses(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=True)
        discord_id = str(ctx.author.id)

        if not check_rate_limit(discord_id, "graph"):
            await ctx.respond(embed=error_embed("Too many chart requests. Wait a minute."))
            return

        try:
            user_id = await require_profile(discord_id)
            image_bytes = await graph_service.generate_income_vs_expenses_chart(user_id)
            file = discord.File(BytesIO(image_bytes), filename="income_vs_expenses.png")
            await ctx.respond(file=file, ephemeral=True)
        except ValueError as e:
            await ctx.respond(embed=error_embed(str(e)))
        except Exception as e:
            logger.error(f"Graph income_vs_expenses failed: {e}", exc_info=True)
            await ctx.respond(embed=error_embed("Failed to generate chart."))


def setup(bot: discord.Bot) -> GraphCommands:
    return GraphCommands(bot)
