from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone

class ChatBase(BaseModel):
    sender_id: int
    receiver_id: int
    message: str

class ChatCreate(ChatBase):
    pass  # sent_at создается автоматически в БД

class ChatRead(ChatBase):
    id: int
    sent_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        from_attributes = True
