import discord
from discord.ext import commands


class HelpCommands(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="help", description="Show all Koin commands and how to use them")
    async def help_command(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(
            title="Koin — Personal Finance Bot",
            description="Your private financial OS inside Discord.",
            color=discord.Color.blurple(),
        )
        embed.add_field(
            name="Getting Started",
            value="`/user create` — Create your profile (required first step)",
            inline=False,
        )
        embed.add_field(
            name="Logging",
            value=(
                "`/spend` — Log an expense\n"
                "`/earn` — Log income\n"
                "`/image` — Upload a receipt for automatic extraction"
            ),
            inline=False,
        )
        embed.add_field(
            name="Debt Tracking",
            value=(
                "`/debt add` — Add a new debt\n"
                "`/debt list` — View all debts\n"
                "`/debt update` — Update a debt's balance"
            ),
            inline=False,
        )
        embed.add_field(
            name="AI Analysis",
            value=(
                "`/ai analyze` — Full financial health report\n"
                "`/ai monthly_plan` — Budget plan for next month\n"
                "`/ai debt_strategy` — Debt payoff recommendation\n"
                "`/ai saving_advice` — Specific saving opportunities"
            ),
            inline=False,
        )
        embed.add_field(
            name="Charts",
            value=(
                "`/graph category_breakdown` — Spending pie chart\n"
                "`/graph income_vs_expenses` — Monthly bar chart"
            ),
            inline=False,
        )
        embed.set_footer(text="All responses are ephemeral (only you can see them).")
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: discord.Bot) -> HelpCommands:
    return HelpCommands(bot)
