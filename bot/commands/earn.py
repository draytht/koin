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

    earn_group = discord.SlashCommandGroup("earn", "Manage income entries")

    @earn_group.command(name="log", description="Log income")
    async def earn_log(
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
            logger.error(f"Earn log command failed: {e}", exc_info=True)
            await ctx.followup.send(embed=error_embed("Something went wrong. Please try again."), ephemeral=True)

    @earn_group.command(name="delete", description="Delete a mistaken income entry")
    async def earn_delete(
        self,
        ctx: discord.ApplicationContext,
        date: discord.Option(str, "Date of the entry (MM-DD-YY)", required=True),
        source: discord.Option(str, "Income source", required=True, choices=INCOME_SOURCES),
        amount: discord.Option(float, "Amount (required if multiple entries match)", required=False),
    ):
        await ctx.defer(ephemeral=True)
        discord_id = str(ctx.author.id)

        try:
            user_id = await require_profile(discord_id)
            from bot.utils.validators import validate_date
            inc_date = validate_date(date)

            matches = await income_service.find_income(user_id, inc_date, source, amount)
            if not matches:
                await ctx.followup.send(embed=error_embed("No matching income entry found."), ephemeral=True)
                return
            if len(matches) > 1:
                await ctx.followup.send(
                    embed=error_embed(
                        f"Found {len(matches)} entries for that date and source. "
                        "Provide the `amount` to narrow it down."
                    ),
                    ephemeral=True,
                )
                return

            entry = matches[0]
            await income_service.delete_income(user_id, entry["id"])
            embed = discord.Embed(
                title="Income Entry Deleted",
                color=discord.Color.orange(),
                description=f"Removed **${entry['amount']:,.2f}** from **{entry['source'].replace('_', ' ').title()}** on {entry['date']}.",
            )
            await ctx.followup.send(embed=embed, ephemeral=True)
        except ValueError as e:
            await ctx.followup.send(embed=error_embed(str(e)), ephemeral=True)
        except Exception as e:
            logger.error(f"Earn delete command failed: {e}", exc_info=True)
            await ctx.followup.send(embed=error_embed("Something went wrong. Please try again."), ephemeral=True)

    @earn_group.command(name="update", description="Correct a logged income entry")
    async def earn_update(
        self,
        ctx: discord.ApplicationContext,
        date: discord.Option(str, "Date of the entry to update (MM-DD-YY)", required=True),
        source: discord.Option(str, "Income source of the entry", required=True, choices=INCOME_SOURCES),
        amount: discord.Option(float, "Current amount (required if multiple entries match)", required=False),
        new_amount: discord.Option(float, "New amount", required=False),
        new_source: discord.Option(str, "New income source", required=False, choices=INCOME_SOURCES),
        new_note: discord.Option(str, "New note", required=False),
        new_date: discord.Option(str, "New date (MM-DD-YY)", required=False),
    ):
        await ctx.defer(ephemeral=True)
        discord_id = str(ctx.author.id)

        try:
            user_id = await require_profile(discord_id)
            from bot.utils.validators import validate_date
            inc_date = validate_date(date)

            updates = {}
            if new_amount is not None:
                updates["amount"] = new_amount
            if new_source is not None:
                updates["source"] = new_source
            if new_note is not None:
                updates["note"] = new_note
            if new_date is not None:
                updates["date"] = validate_date(new_date).isoformat()

            if not updates:
                await ctx.followup.send(embed=error_embed("Provide at least one field to update."), ephemeral=True)
                return

            matches = await income_service.find_income(user_id, inc_date, source, amount)
            if not matches:
                await ctx.followup.send(embed=error_embed("No matching income entry found."), ephemeral=True)
                return
            if len(matches) > 1:
                await ctx.followup.send(
                    embed=error_embed(
                        f"Found {len(matches)} entries for that date and source. "
                        "Provide the `amount` to narrow it down."
                    ),
                    ephemeral=True,
                )
                return

            entry = matches[0]
            result = await income_service.update_income(user_id, entry["id"], updates)
            embed = discord.Embed(title="Income Entry Updated", color=discord.Color.blue())
            embed.add_field(name="Amount", value=f"${result['amount']:,.2f}", inline=True)
            embed.add_field(name="Source", value=result["source"].replace("_", " ").title(), inline=True)
            embed.add_field(name="Date", value=result["date"], inline=True)
            if result.get("note"):
                embed.add_field(name="Note", value=result["note"], inline=False)
            await ctx.followup.send(embed=embed, ephemeral=True)
        except ValueError as e:
            await ctx.followup.send(embed=error_embed(str(e)), ephemeral=True)
        except Exception as e:
            logger.error(f"Earn update command failed: {e}", exc_info=True)
            await ctx.followup.send(embed=error_embed("Something went wrong. Please try again."), ephemeral=True)


def setup(bot: discord.Bot) -> EarnCommands:
    return EarnCommands(bot)
