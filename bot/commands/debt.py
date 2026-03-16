import logging
import discord
from discord.ext import commands
from bot.middleware.rate_limiter import check_rate_limit
from bot.middleware.user_guard import require_profile
from bot.services import debt_service
from bot.models.debt import DebtCreate
from bot.utils.formatters import debt_list_embed, error_embed

logger = logging.getLogger(__name__)


class DebtCommands(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    debt_group = discord.SlashCommandGroup("debt", "Track your debts")

    @debt_group.command(name="add", description="Add a new debt to track")
    async def debt_add(
        self,
        ctx: discord.ApplicationContext,
        debt_name: discord.Option(str, "Name for this debt (e.g. Visa, Student Loan)", required=True),
        creditor: discord.Option(str, "Who you owe (e.g. Chase, Sallie Mae)", required=True),
        total_amount: discord.Option(float, "Original total amount", required=True),
        interest_rate: discord.Option(float, "Annual interest rate as % (e.g. 19.99)", required=True),
        minimum_payment: discord.Option(float, "Monthly minimum payment", required=True),
        due_date: discord.Option(str, "Payment due date (YYYY-MM-DD)", required=False),
        note: discord.Option(str, "Optional note", required=False),
    ):
        await ctx.defer(ephemeral=True)
        discord_id = str(ctx.author.id)

        if not check_rate_limit(discord_id, "debt"):
            await ctx.respond(embed=error_embed("Too many requests. Try again in a minute."))
            return

        try:
            user_id = await require_profile(discord_id)
            from bot.utils.validators import validate_date
            parsed_due = validate_date(due_date) if due_date else None

            data = DebtCreate(
                debt_name=debt_name,
                creditor=creditor,
                total_amount=total_amount,
                interest_rate=interest_rate,
                minimum_payment=minimum_payment,
                due_date=parsed_due,
                note=note,
            )
            result = await debt_service.add_debt(user_id, data)
            embed = discord.Embed(
                title="Debt Added",
                color=discord.Color.red(),
            )
            embed.add_field(name="Name", value=result["debt_name"], inline=True)
            embed.add_field(name="Creditor", value=result["creditor"], inline=True)
            embed.add_field(name="Total Amount", value=f"${result['total_amount']:,.2f}", inline=True)
            embed.add_field(name="Rate", value=f"{result['interest_rate']*100:.2f}% APR", inline=True)
            embed.add_field(name="Min Payment", value=f"${result['minimum_payment']:,.2f}/mo", inline=True)
            await ctx.respond(embed=embed)
        except ValueError as e:
            await ctx.respond(embed=error_embed(str(e)))

    @debt_group.command(name="list", description="View all your tracked debts")
    async def debt_list(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=True)
        try:
            user_id = await require_profile(str(ctx.author.id))
            debts = await debt_service.list_debts(user_id)
            embed = debt_list_embed(debts)
            await ctx.respond(embed=embed)
        except ValueError as e:
            await ctx.respond(embed=error_embed(str(e)))

    @debt_group.command(name="update", description="Update a debt's details or correct wrong input")
    async def debt_update(
        self,
        ctx: discord.ApplicationContext,
        debt_name: discord.Option(str, "Name of the debt to update", required=True),
        total_amount: discord.Option(float, "Correct the original total amount", required=False),
        current_balance: discord.Option(float, "Update current balance", required=False),
        interest_rate: discord.Option(float, "New annual interest rate as % (e.g. 19.99)", required=False),
        minimum_payment: discord.Option(float, "New minimum payment", required=False),
        note: discord.Option(str, "Updated note", required=False),
    ):
        await ctx.defer(ephemeral=True)
        try:
            user_id = await require_profile(str(ctx.author.id))
            updates = {}
            if total_amount is not None:
                updates["total_amount"] = total_amount
            if current_balance is not None:
                updates["current_balance"] = current_balance
            if interest_rate is not None:
                updates["interest_rate"] = interest_rate
            if minimum_payment is not None:
                updates["minimum_payment"] = minimum_payment
            if note is not None:
                updates["note"] = note
            if not updates:
                await ctx.respond(embed=error_embed("Provide at least one field to update."))
                return
            result = await debt_service.update_debt(user_id, debt_name, updates)
            embed = discord.Embed(title=f"Debt Updated: {debt_name}", color=discord.Color.orange())
            embed.add_field(name="Total Amount", value=f"${result['total_amount']:,.2f}", inline=True)
            embed.add_field(name="Current Balance", value=f"${result['current_balance']:,.2f}", inline=True)
            embed.add_field(name="Rate", value=f"{result['interest_rate']*100:.2f}% APR", inline=True)
            embed.add_field(name="Min Payment", value=f"${result['minimum_payment']:,.2f}/mo", inline=True)
            await ctx.respond(embed=embed)
        except ValueError as e:
            await ctx.respond(embed=error_embed(str(e)))
        except Exception as e:
            logger.error(f"Debt update command failed: {e}", exc_info=True)
            await ctx.respond(embed=error_embed("Something went wrong. Please try again."))

    @debt_group.command(name="delete", description="Delete a mistakenly added debt")
    async def debt_delete(
        self,
        ctx: discord.ApplicationContext,
        debt_name: discord.Option(str, "Name of the debt to delete", required=True),
    ):
        await ctx.defer(ephemeral=True)
        try:
            user_id = await require_profile(str(ctx.author.id))
            await debt_service.delete_debt(user_id, debt_name)
            embed = discord.Embed(
                title="Debt Deleted",
                color=discord.Color.orange(),
                description=f"Removed debt **{debt_name}** from your records.",
            )
            await ctx.respond(embed=embed)
        except ValueError as e:
            await ctx.respond(embed=error_embed(str(e)))
        except Exception as e:
            logger.error(f"Debt delete command failed: {e}", exc_info=True)
            await ctx.respond(embed=error_embed("Something went wrong. Please try again."))


def setup(bot: discord.Bot) -> DebtCommands:
    return DebtCommands(bot)
