import logging
import discord
from discord.ext import commands
from bot.middleware.rate_limiter import check_rate_limit
from bot.middleware.user_guard import require_profile
from bot.services import saving_service
from bot.models.saving import SavingCreate
from bot.utils.formatters import (
    saving_embed, saving_list_embed,
    saving_deleted_embed, saving_updated_embed,
    error_embed,
)
from bot.utils.validators import validate_date

logger = logging.getLogger(__name__)


class SaveCommands(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    save_group = discord.SlashCommandGroup("save", "Manage your savings")

    @save_group.command(name="log", description="Log a saving")
    async def save_log(
        self,
        ctx: discord.ApplicationContext,
        amount: discord.Option(float, "Amount saved", required=True),
        goal: discord.Option(str, "What are you saving for?", required=True),
        note: discord.Option(str, "Optional note", required=False),
        date: discord.Option(str, "Date (MM-DD-YY, default: today)", required=False),
    ):
        await ctx.defer(ephemeral=True)
        discord_id = str(ctx.author.id)

        if not check_rate_limit(discord_id, "save"):
            await ctx.followup.send(embed=error_embed("Slow down! Try again in a minute."), ephemeral=True)
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
            await ctx.followup.send(embed=embed, ephemeral=True)
        except ValueError as e:
            await ctx.followup.send(embed=error_embed(str(e)), ephemeral=True)
        except Exception as e:
            logger.error(f"Save log failed: {e}", exc_info=True)
            await ctx.followup.send(embed=error_embed("Something went wrong. Please try again."), ephemeral=True)

    @save_group.command(name="list", description="View your recent savings")
    async def save_list(
        self,
        ctx: discord.ApplicationContext,
        limit: discord.Option(int, "Number of entries to show (default: 10, max: 25)", required=False, default=10),
    ):
        await ctx.defer(ephemeral=True)
        try:
            user_id = await require_profile(str(ctx.author.id))
            limit = max(1, min(limit, 25))
            savings = await saving_service.list_savings(user_id, limit=limit)
            await ctx.followup.send(embed=saving_list_embed(savings), ephemeral=True)
        except ValueError as e:
            await ctx.followup.send(embed=error_embed(str(e)), ephemeral=True)
        except Exception as e:
            logger.error(f"Save list failed: {e}", exc_info=True)
            await ctx.followup.send(embed=error_embed("Something went wrong. Please try again."), ephemeral=True)

    @save_group.command(name="delete", description="Delete a mistaken saving entry")
    async def save_delete(
        self,
        ctx: discord.ApplicationContext,
        date: discord.Option(str, "Date of the entry (MM-DD-YY)", required=True),
        goal: discord.Option(str, "Goal of the entry", required=True),
        amount: discord.Option(float, "Amount (required if multiple entries match)", required=False),
    ):
        await ctx.defer(ephemeral=True)
        try:
            user_id = await require_profile(str(ctx.author.id))
            save_date = validate_date(date)

            matches = await saving_service.find_saving(user_id, save_date, goal, amount)
            if not matches:
                await ctx.followup.send(embed=error_embed("No matching saving entry found."), ephemeral=True)
                return
            if len(matches) > 1:
                await ctx.followup.send(
                    embed=error_embed(
                        f"Found {len(matches)} entries for that date and goal. "
                        "Provide the `amount` to narrow it down."
                    ),
                    ephemeral=True,
                )
                return

            entry = matches[0]
            await saving_service.delete_saving(user_id, entry["id"])
            await ctx.followup.send(embed=saving_deleted_embed(entry), ephemeral=True)
        except ValueError as e:
            await ctx.followup.send(embed=error_embed(str(e)), ephemeral=True)
        except Exception as e:
            logger.error(f"Save delete failed: {e}", exc_info=True)
            await ctx.followup.send(embed=error_embed("Something went wrong. Please try again."), ephemeral=True)

    @save_group.command(name="update", description="Correct a saving entry")
    async def save_update(
        self,
        ctx: discord.ApplicationContext,
        date: discord.Option(str, "Date of the entry to update (MM-DD-YY)", required=True),
        goal: discord.Option(str, "Goal of the entry", required=True),
        amount: discord.Option(float, "Current amount (required if multiple entries match)", required=False),
        new_amount: discord.Option(float, "New amount", required=False),
        new_goal: discord.Option(str, "New goal description", required=False),
        new_note: discord.Option(str, "New note", required=False),
        new_date: discord.Option(str, "New date (MM-DD-YY)", required=False),
    ):
        await ctx.defer(ephemeral=True)
        try:
            user_id = await require_profile(str(ctx.author.id))
            save_date = validate_date(date)

            updates = {}
            if new_amount is not None:
                updates["amount"] = new_amount
            if new_goal is not None:
                updates["goal"] = new_goal
            if new_note is not None:
                updates["note"] = new_note
            if new_date is not None:
                updates["date"] = validate_date(new_date).isoformat()

            if not updates:
                await ctx.followup.send(embed=error_embed("Provide at least one field to update."), ephemeral=True)
                return

            matches = await saving_service.find_saving(user_id, save_date, goal, amount)
            if not matches:
                await ctx.followup.send(embed=error_embed("No matching saving entry found."), ephemeral=True)
                return
            if len(matches) > 1:
                await ctx.followup.send(
                    embed=error_embed(
                        f"Found {len(matches)} entries for that date and goal. "
                        "Provide the `amount` to narrow it down."
                    ),
                    ephemeral=True,
                )
                return

            entry = matches[0]
            result = await saving_service.update_saving(user_id, entry["id"], updates)
            await ctx.followup.send(embed=saving_updated_embed(result), ephemeral=True)
        except ValueError as e:
            await ctx.followup.send(embed=error_embed(str(e)), ephemeral=True)
        except Exception as e:
            logger.error(f"Save update failed: {e}", exc_info=True)
            await ctx.followup.send(embed=error_embed("Something went wrong. Please try again."), ephemeral=True)


def setup(bot: discord.Bot) -> SaveCommands:
    return SaveCommands(bot)
