from pydantic import BaseModel
from datetime import date, datetime
from uuid import UUID
from typing import Optional, Any


class Receipt(BaseModel):
    id: UUID
    user_id: UUID
    storage_path: str
    ocr_raw_text: Optional[str] = None
    parsed_merchant: Optional[str] = None
    parsed_total: Optional[float] = None
    parsed_date: Optional[date] = None
    parsed_tax: Optional[float] = None
    parsed_items: Optional[Any] = None
    confidence: Optional[float] = None
    confirmed: bool = False
    created_at: datetime
