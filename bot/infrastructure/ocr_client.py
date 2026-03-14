import asyncio
import logging
from io import BytesIO
from PIL import Image
from bot.config import config

logger = logging.getLogger(__name__)


def _tesseract_extract(image_bytes: bytes) -> tuple[str, float]:
    """Returns (raw_text, confidence_score)."""
    import pytesseract
    image = Image.open(BytesIO(image_bytes))
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    confidences = [int(c) for c in data["conf"] if str(c).isdigit() and int(c) >= 0]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    text = pytesseract.image_to_string(image)
    return text, round(avg_confidence / 100, 2)


async def extract_text(image_bytes: bytes) -> tuple[str, float]:
    """Extract text from image. Returns (raw_text, confidence 0-1)."""
    if config.OCR_PROVIDER == "tesseract":
        return await asyncio.to_thread(_tesseract_extract, image_bytes)
    raise NotImplementedError(f"OCR provider '{config.OCR_PROVIDER}' not implemented")
