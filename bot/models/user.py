from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class User(BaseModel):
    id: UUID
    discord_id: str
    username: str
    currency: str = "USD"
    timezone: str = "UTC"
    created_at: datetime
    updated_at: datetime
