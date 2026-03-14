import discord
import logging
from bot.config import config
from bot.commands import user, spend, earn, debt, image, ai_commands, graph, help, save

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("koin")

intents = discord.Intents.default()
bot = discord.Bot(
    intents=intents,
    debug_guilds=[config.DISCORD_GUILD_ID] if config.DISCORD_GUILD_ID else None,
)

# Register cogs
cogs = [user, spend, earn, debt, image, ai_commands, graph, help, save]
for cog_module in cogs:
    bot.add_cog(cog_module.setup(bot))


@bot.event
async def on_ready():
    logger.info(f"Koin bot online as {bot.user} (ID: {bot.user.id})")


@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: Exception):
    if isinstance(error, discord.ApplicationCommandInvokeError):
        error = error.original
    logger.error(f"Command error in {ctx.command}: {error}", exc_info=error)
    if not ctx.response.is_done():
        await ctx.respond("Something went wrong. Please try again.", ephemeral=True)
    else:
        await ctx.followup.send("Something went wrong. Please try again.", ephemeral=True)


if __name__ == "__main__":
    bot.run(config.DISCORD_TOKEN)
