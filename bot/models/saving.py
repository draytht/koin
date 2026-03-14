from pydantic import BaseModel
from datetime import date as date_type
from uuid import UUID
from typing import Optional


class Saving(BaseModel):
    id: UUID
    user_id: UUID
    amount: float
    goal: str
    note: Optional[str] = None
    date: date_type


class SavingCreate(BaseModel):
    amount: float
    goal: str
    note: Optional[str] = None
    date: Optional[date_type] = None
