import discord
from discord.ext import commands
from bot.middleware.rate_limiter import check_rate_limit
from bot.middleware.user_guard import require_profile
from bot.services import receipt_service, expense_service
from bot.models.expense import ExpenseCreate
from bot.utils.formatters import receipt_preview_embed, error_embed
from bot.utils.validators import EXPENSE_CATEGORIES
import logging

logger = logging.getLogger(__name__)


class ImageCommands(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="image", description="Upload a receipt image to extract and log as an expense")
    async def image(
        self,
        ctx: discord.ApplicationContext,
        receipt: discord.Option(discord.Attachment, "Receipt image (jpg, png, webp, pdf)", required=True),
        category: discord.Option(str, "Expense category", required=False, choices=EXPENSE_CATEGORIES, default="other"),
    ):
        await ctx.defer(ephemeral=True)
        discord_id = str(ctx.author.id)

        if not check_rate_limit(discord_id, "image"):
            await ctx.respond(embed=error_embed("Too many image uploads. Wait a minute and try again."))
            return

        try:
            user_id = await require_profile(discord_id)
            await ctx.followup.send("Processing your receipt...", ephemeral=True)

            # Download attachment
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(receipt.url) as resp:
                    image_bytes = await resp.read()

            parsed = await receipt_service.process_receipt(user_id, image_bytes)
            receipt_id = parsed["receipt_id"]

            if parsed.get("confidence", 1.0) < 0.5 and not parsed.get("total"):
                await ctx.followup.send(
                    embed=error_embed(
                        "Couldn't read this receipt clearly. Please log it manually with `/spend`."
                    ),
                    ephemeral=True,
                )
                return

            embed = receipt_preview_embed(parsed)

            # Confirmation buttons
            confirm_view = ReceiptConfirmView(
                receipt_id=receipt_id,
                user_id=user_id,
                parsed=parsed,
                category=category,
            )
            await ctx.followup.send(embed=embed, view=confirm_view, ephemeral=True)

        except ValueError as e:
            await ctx.followup.send(embed=error_embed(str(e)), ephemeral=True)
        except Exception as e:
            logger.error(f"Image command failed: {e}", exc_info=True)
            await ctx.followup.send(
                embed=error_embed("Failed to process receipt. Please log manually with `/spend`."),
                ephemeral=True,
            )


class ReceiptConfirmView(discord.ui.View):
    def __init__(self, receipt_id: str, user_id: str, parsed: dict, category: str):
        super().__init__(timeout=300)  # 5 minute window
        self.receipt_id = receipt_id
        self.user_id = user_id
        self.parsed = parsed
        self.category = category

    @discord.ui.button(label="Save", style=discord.ButtonStyle.success, emoji="✅")
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            await receipt_service.confirm_receipt(self.receipt_id, self.user_id)

            from datetime import date
            from bot.utils.validators import validate_date
            exp_date = validate_date(self.parsed.get("date"))

            data = ExpenseCreate(
                amount=self.parsed.get("total") or 0.01,
                category=self.category,
                merchant=self.parsed.get("merchant"),
                date=exp_date,
                recurring=False,
            )
            from bot.services import expense_service
            result = await expense_service.log_expense(self.user_id, data)

            embed = discord.Embed(
                title="Receipt Saved",
                description=f"Logged **${result['amount']:,.2f}** at {result.get('merchant') or 'Unknown'} ({self.category})",
                color=discord.Color.green(),
            )
            self.disable_all_items()
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.followup.send(embed=error_embed(str(e)), ephemeral=True)

    @discord.ui.button(label="Discard", style=discord.ButtonStyle.danger, emoji="❌")
    async def discard(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.disable_all_items()
        await interaction.response.send_message("Receipt discarded.", ephemeral=True)


def setup(bot: discord.Bot) -> ImageCommands:
    return ImageCommands(bot)
