from pydantic import BaseModel
from datetime import date
from uuid import UUID
from typing import Optional


class Debt(BaseModel):
    id: UUID
    user_id: UUID
    debt_name: str
    creditor: str
    total_amount: float
    current_balance: float
    interest_rate: float
    minimum_payment: float
    due_date: Optional[date] = None
    note: Optional[str] = None
    is_paid_off: bool = False


class DebtCreate(BaseModel):
    debt_name: str
    creditor: str
    total_amount: float
    interest_rate: float
    minimum_payment: float
    due_date: Optional[date] = None
    note: Optional[str] = None
