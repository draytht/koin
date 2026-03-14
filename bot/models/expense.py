from pydantic import BaseModel, field_validator
from datetime import date as date_type
from uuid import UUID
from typing import Optional


class Expense(BaseModel):
    id: UUID
    user_id: UUID
    amount: float
    category: str
    merchant: Optional[str] = None
    note: Optional[str] = None
    payment_method: Optional[str] = None
    date: date_type
    recurring: bool = False
    receipt_id: Optional[UUID] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v


class ExpenseCreate(BaseModel):
    amount: float
    category: str
    merchant: Optional[str] = None
    note: Optional[str] = None
    payment_method: Optional[str] = None
    date: Optional[date_type] = None
    recurring: bool = False
