import discord
from discord.ext import commands
from bot.utils.formatters import COLOR_INFO


class HelpCommands(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="help", description="Show all Koin commands")
    async def help_command(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(
            title="📖  Koin — Command Reference",
            description="Your personal finance OS inside Discord.\nAll responses are private — only you can see them.",
            color=COLOR_INFO,
        )

        embed.add_field(
            name="🚀  Getting Started",
            value="`/user create` — Create your profile *(required first)*\n`/user profile` — View your financial overview",
            inline=False,
        )
        embed.add_field(
            name="🧾  Expenses",
            value=(
                "`/spend` — Log an expense\n"
            ),
            inline=True,
        )
        embed.add_field(
            name="💰  Income",
            value=(
                "`/earn log` — Log income\n"
                "`/earn update` — Correct an entry\n"
                "`/earn delete` — Remove an entry"
            ),
            inline=True,
        )
        embed.add_field(name="\u200b", value="\u200b", inline=True)

        embed.add_field(
            name="🏦  Savings",
            value=(
                "`/save log` — Log a saving\n"
                "`/save list` — View recent savings\n"
                "`/save update` — Correct an entry\n"
                "`/save delete` — Remove an entry"
            ),
            inline=True,
        )
        embed.add_field(
            name="🔴  Debt Tracker",
            value=(
                "`/debt add` — Add a debt\n"
                "`/debt list` — View all debts\n"
                "`/debt update` — Correct details\n"
                "`/debt delete` — Remove a debt"
            ),
            inline=True,
        )
        embed.add_field(name="\u200b", value="\u200b", inline=True)

        embed.add_field(
            name="🤖  AI Analysis",
            value=(
                "`/ai analyze` — Full financial health report\n"
                "`/ai monthly_plan` — Budget plan for next month\n"
                "`/ai debt_strategy` — Debt payoff recommendation\n"
                "`/ai saving_advice` — Saving opportunities"
            ),
            inline=False,
        )
        embed.add_field(
            name="📊  Charts",
            value=(
                "`/graph category_breakdown` — Spending pie chart\n"
                "`/graph income_vs_expenses` — Monthly bar chart"
            ),
            inline=False,
        )
        embed.add_field(
            name="🖼️  Receipts",
            value="`/image` — Upload a receipt for automatic extraction",
            inline=False,
        )

        embed.set_footer(text="💡  Tip: all dates accept MM-DD-YY format, or just leave blank for today.")
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: discord.Bot) -> HelpCommands:
    return HelpCommands(bot)
