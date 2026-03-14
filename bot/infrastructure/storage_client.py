import logging
import uuid
from bot.infrastructure.supabase_client import get_supabase

logger = logging.getLogger(__name__)

BUCKET = "receipts"


async def upload_receipt(image_bytes: bytes, content_type: str) -> str:
    """Upload image to Supabase Storage. Returns storage path."""
    import asyncio
    supabase = get_supabase()
    filename = f"{uuid.uuid4()}.{'jpg' if 'jpeg' in content_type else 'png'}"
    path = f"receipts/{filename}"

    def _upload():
        return supabase.storage.from_(BUCKET).upload(
            path, image_bytes, {"content-type": content_type, "upsert": "false"}
        )

    await asyncio.to_thread(_upload)
    return path


async def delete_receipt(path: str) -> None:
    import asyncio
    supabase = get_supabase()

    def _delete():
        return supabase.storage.from_(BUCKET).remove([path])

    await asyncio.to_thread(_delete)
