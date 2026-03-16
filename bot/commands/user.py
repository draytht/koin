import discord
from discord.ext import commands
from bot.services import user_service
from bot.utils.formatters import user_created_embed, user_profile_embed, error_embed


class UserCommands(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    user_group = discord.SlashCommandGroup("user", "Manage your profile")

    @user_group.command(name="create", description="Create your finance profile")
    async def user_create(
        self,
        ctx: discord.ApplicationContext,
        currency: discord.Option(str, "Your preferred currency (default: USD)", required=False, default="USD"),
        timezone: discord.Option(str, "Your timezone (default: UTC)", required=False, default="UTC"),
    ):
        await ctx.defer(ephemeral=True)
        try:
            user = await user_service.create_user(
                discord_id=str(ctx.author.id),
                username=ctx.author.name,
                currency=currency.upper(),
                timezone=timezone,
            )
            await ctx.respond(embed=user_created_embed(user.username, user.currency, user.timezone))
        except ValueError as e:
            await ctx.respond(embed=error_embed(str(e)))

    @user_group.command(name="profile", description="View your profile")
    async def user_profile(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=True)
        try:
            user = await user_service.get_user_profile(str(ctx.author.id))
            if not user:
                await ctx.followup.send(embed=error_embed("No profile found. Run `/user create` first."))
                return
            await ctx.followup.send(embed=user_profile_embed(user, ctx.author.display_avatar.url))
        except Exception as e:
            await ctx.followup.send(embed=error_embed(f"Failed to fetch profile: {e}"))


def setup(bot: discord.Bot) -> UserCommands:
    return UserCommands(bot)
