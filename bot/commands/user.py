import discord
from discord.ext import commands
from bot.services import user_service
from bot.utils.formatters import error_embed


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
            embed = discord.Embed(
                title="Profile Created!",
                description=f"Welcome to Koin, {user.username}! Your financial OS is ready.",
                color=discord.Color.green(),
            )
            embed.add_field(name="Currency", value=user.currency, inline=True)
            embed.add_field(name="Timezone", value=user.timezone, inline=True)
            embed.set_footer(text="Run /help to see all commands.")
            await ctx.respond(embed=embed)
        except ValueError as e:
            await ctx.respond(embed=error_embed(str(e)))

    @user_group.command(name="profile", description="View your profile")
    async def user_profile(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=True)
        user = await user_service.get_user(str(ctx.author.id))
        if not user:
            await ctx.respond(embed=error_embed("No profile found. Run `/user create` first."))
            return
        embed = discord.Embed(title="Your Profile", color=discord.Color.blurple())
        embed.add_field(name="Username", value=user.username, inline=True)
        embed.add_field(name="Currency", value=user.currency, inline=True)
        embed.add_field(name="Timezone", value=user.timezone, inline=True)
        embed.set_footer(text=f"Member since {user.created_at.strftime('%b %d, %Y')}")
        await ctx.respond(embed=embed)


def setup(bot: discord.Bot) -> UserCommands:
    return UserCommands(bot)
