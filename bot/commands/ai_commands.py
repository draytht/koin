import discord
from discord.ext import commands
from bot.middleware.rate_limiter import check_rate_limit
from bot.middleware.user_guard import require_profile
from bot.services import ai_service
from bot.utils.formatters import error_embed
import logging

logger = logging.getLogger(__name__)


class AICommands(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    ai_group = discord.SlashCommandGroup("ai", "AI-powered financial analysis")

    @ai_group.command(name="analyze", description="Full financial health analysis (last 30 days)")
    async def ai_analyze(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=True)
        discord_id = str(ctx.author.id)

        if not check_rate_limit(discord_id, "ai"):
            await ctx.respond(embed=error_embed("AI rate limit reached. Wait a few minutes."))
            return

        try:
            user_id = await require_profile(discord_id)
            await ctx.followup.send("Analyzing your finances...", ephemeral=True)
            response = await ai_service.analyze(user_id, "full financial health analysis")
            embed = discord.Embed(title="Financial Analysis", description=response, color=discord.Color.blurple())
            embed.set_footer(text="Based on last 30 days of data")
            await ctx.followup.send(embed=embed, ephemeral=True)
        except ValueError as e:
            await ctx.followup.send(embed=error_embed(str(e)), ephemeral=True)
        except Exception as e:
            logger.error(f"AI analyze failed: {e}", exc_info=True)
            await ctx.followup.send(embed=error_embed("AI analysis failed. Try again later."), ephemeral=True)

    @ai_group.command(name="monthly_plan", description="Get a suggested budget plan for next month")
    async def ai_monthly_plan(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=True)
        discord_id = str(ctx.author.id)

        if not check_rate_limit(discord_id, "ai"):
            await ctx.respond(embed=error_embed("AI rate limit reached. Wait a few minutes."))
            return

        try:
            user_id = await require_profile(discord_id)
            await ctx.followup.send("Building your monthly plan...", ephemeral=True)
            response = await ai_service.analyze(user_id, "suggested monthly budget plan for next month", days=90)
            embed = discord.Embed(title="Monthly Budget Plan", description=response, color=discord.Color.gold())
            embed.set_footer(text="Based on last 90 days of data")
            await ctx.followup.send(embed=embed, ephemeral=True)
        except ValueError as e:
            await ctx.followup.send(embed=error_embed(str(e)), ephemeral=True)

    @ai_group.command(name="debt_strategy", description="Get a debt payoff strategy")
    async def ai_debt_strategy(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=True)
        discord_id = str(ctx.author.id)

        if not check_rate_limit(discord_id, "ai"):
            await ctx.respond(embed=error_embed("AI rate limit reached. Wait a few minutes."))
            return

        try:
            user_id = await require_profile(discord_id)
            await ctx.followup.send("Calculating debt strategy...", ephemeral=True)
            response = await ai_service.analyze(user_id, "debt payoff strategy: compare avalanche vs snowball, recommend best approach for this debt profile")
            embed = discord.Embed(title="Debt Payoff Strategy", description=response, color=discord.Color.red())
            await ctx.followup.send(embed=embed, ephemeral=True)
        except ValueError as e:
            await ctx.followup.send(embed=error_embed(str(e)), ephemeral=True)

    @ai_group.command(name="saving_advice", description="Get personalized saving suggestions")
    async def ai_saving_advice(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=True)
        discord_id = str(ctx.author.id)

        if not check_rate_limit(discord_id, "ai"):
            await ctx.respond(embed=error_embed("AI rate limit reached. Wait a few minutes."))
            return

        try:
            user_id = await require_profile(discord_id)
            await ctx.followup.send("Finding saving opportunities...", ephemeral=True)
            response = await ai_service.analyze(user_id, "identify specific saving opportunities and suggest concrete monthly savings targets")
            embed = discord.Embed(title="Saving Advice", description=response, color=discord.Color.green())
            await ctx.followup.send(embed=embed, ephemeral=True)
        except ValueError as e:
            await ctx.followup.send(embed=error_embed(str(e)), ephemeral=True)


def setup(bot: discord.Bot) -> AICommands:
    return AICommands(bot)
