import magic
from datetime import date

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

EXPENSE_CATEGORIES = [
    "food", "transport", "housing", "entertainment",
    "health", "shopping", "utilities", "education", "other"
]

PAYMENT_METHODS = ["cash", "debit", "credit", "transfer", "other"]

INCOME_SOURCES = ["paycheck", "freelance", "gift", "investment", "side_hustle", "other"]


def validate_image(data: bytes) -> str:
    """Validate image bytes. Returns MIME type or raises ValueError."""
    if len(data) > MAX_FILE_SIZE:
        raise ValueError(f"File too large. Maximum size is 10MB.")
    mime = magic.from_buffer(data, mime=True)
    if mime not in ALLOWED_MIME_TYPES:
        raise ValueError(f"Unsupported file type: {mime}. Allowed: jpg, png, webp, pdf.")
    return mime


def validate_amount(amount: float) -> float:
    if amount <= 0:
        raise ValueError("Amount must be greater than 0.")
    if amount >= 1_000_000:
        raise ValueError("Amount must be less than 1,000,000.")
    return round(amount, 2)


def validate_date(date_str: str | None) -> date:
    if date_str is None:
        return date.today()
    try:
        parsed = date.fromisoformat(date_str)
        if parsed > date.today():
            raise ValueError("Date cannot be in the future.")
        return parsed
    except ValueError as e:
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD. {e}")
