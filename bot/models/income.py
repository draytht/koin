from pydantic import BaseModel
from datetime import date
from uuid import UUID
from typing import Optional


class Income(BaseModel):
    id: UUID
    user_id: UUID
    amount: float
    source: str
    note: Optional[str] = None
    date: date


class IncomeCreate(BaseModel):
    amount: float
    source: str
    note: Optional[str] = None
    date: Optional[date] = None
