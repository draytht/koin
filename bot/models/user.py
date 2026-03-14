from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


class User(BaseModel):
    id: UUID
    discord_id: str
    username: str
    currency: str = "USD"
    timezone: str = "UTC"
    created_at: datetime
    updated_at: datetime
    # computed fields populated by get_user_profile
    total_income: float = 0.0
    total_expenses: float = 0.0
    total_debts: float = 0.0
    total_savings: float = 0.0
    net_worth: float = 0.0
    monthly_budget: float = 0.0
    financial_health: str = "N/A"
    ai_insights: Optional[str] = None
