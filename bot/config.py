import os
from dotenv import load_dotenv

load_dotenv()


def _require(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value


class Config:
    DISCORD_TOKEN: str = _require("DISCORD_TOKEN")
    DISCORD_GUILD_ID: int | None = int(os.getenv("DISCORD_GUILD_ID", 0)) or None

    SUPABASE_URL: str = _require("SUPABASE_URL")
    SUPABASE_SERVICE_KEY: str = _require("SUPABASE_SERVICE_KEY")

    ANTHROPIC_API_KEY: str = _require("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5")

    OCR_PROVIDER: str = os.getenv("OCR_PROVIDER", "tesseract")
    GOOGLE_VISION_API_KEY: str = os.getenv("GOOGLE_VISION_API_KEY", "")

    OWNER_DISCORD_ID: str = os.getenv("OWNER_DISCORD_ID", "")

    # Rate limits: (max_calls, window_seconds)
    RATE_LIMITS: dict = {
        "spend": (10, 60),
        "earn": (10, 60),
        "debt": (10, 60),
        "image": (3, 60),
        "ai": (5, 300),
        "graph": (5, 60),
        "save": (10, 60),
    }


config = Config()
