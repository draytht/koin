import asyncio
import json
import logging
import re
from bot.infrastructure.ocr_client import extract_text
from bot.infrastructure.llm_client import chat_completion
from bot.infrastructure.storage_client import upload_receipt
from bot.infrastructure.supabase_client import get_supabase
from bot.utils.validators import validate_image

logger = logging.getLogger(__name__)

OCR_CONFIDENCE_THRESHOLD = 0.5

_EXTRACTION_SYSTEM = (
    "You are a receipt data extractor. Extract structured data from receipt text. "
    "Return ONLY valid JSON with these fields: merchant (string or null), total (float or null), "
    "date (string YYYY-MM-DD or null), tax (float or null), items (array of {name, price} or []). "
    "Do not add commentary."
)


async def process_receipt(user_id: str, image_bytes: bytes) -> dict:
    """Full pipeline: validate → upload → OCR → AI parse. Returns parsed data + receipt_id."""
    # Validate
    mime_type = validate_image(image_bytes)

    # Upload to storage
    storage_path = await upload_receipt(image_bytes, mime_type)

    # OCR
    raw_text, confidence = await extract_text(image_bytes)
    logger.info(f"OCR confidence: {confidence:.2f}")

    if confidence < OCR_CONFIDENCE_THRESHOLD:
        logger.warning(f"Low OCR confidence ({confidence:.2f}) for receipt")

    # Clean text
    cleaned = _clean_ocr_text(raw_text)

    # AI extraction
    parsed = await _extract_with_ai(cleaned)
    parsed["confidence"] = confidence

    # Store receipt row (unconfirmed)
    receipt_id = await _save_receipt_row(user_id, storage_path, raw_text, parsed)
    parsed["receipt_id"] = receipt_id

    return parsed


async def confirm_receipt(receipt_id: str, user_id: str) -> dict:
    """Mark receipt as confirmed. Returns receipt data."""
    supabase = get_supabase()

    def _update():
        return (
            supabase.table("receipts")
            .update({"confirmed": True})
            .eq("id", receipt_id)
            .eq("user_id", user_id)
            .execute()
        )

    result = await asyncio.to_thread(_update)
    if not result.data:
        raise ValueError("Receipt not found or unauthorized.")
    return result.data[0]


async def _save_receipt_row(user_id: str, storage_path: str, raw_text: str, parsed: dict) -> str:
    supabase = get_supabase()
    row = {
        "user_id": user_id,
        "storage_path": storage_path,
        "ocr_raw_text": raw_text[:5000],  # limit stored raw text
        "parsed_merchant": parsed.get("merchant"),
        "parsed_total": parsed.get("total"),
        "parsed_date": parsed.get("date"),
        "parsed_tax": parsed.get("tax"),
        "parsed_items": parsed.get("items"),
        "confidence": parsed.get("confidence"),
        "confirmed": False,
    }

    def _insert():
        return supabase.table("receipts").insert(row).execute()

    result = await asyncio.to_thread(_insert)
    return result.data[0]["id"]


def _clean_ocr_text(raw: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", raw)
    text = re.sub(r"[^\x20-\x7E\n]", "", text)
    return text.strip()


async def _extract_with_ai(cleaned_text: str) -> dict:
    user_prompt = f"Receipt text:\n{cleaned_text[:3000]}"
    try:
        response = await chat_completion(_EXTRACTION_SYSTEM, user_prompt, temperature=0.1)
        # Extract JSON from response
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        logger.error(f"AI receipt extraction failed: {e}")
    return {"merchant": None, "total": None, "date": None, "tax": None, "items": []}
