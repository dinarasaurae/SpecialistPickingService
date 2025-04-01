from pydantic import BaseModel
from datetime import datetime

class ReviewBase(BaseModel):
    client_id: int
    psychologist_id: int
    rating: int
    comment: str | None = None

class ReviewRead(ReviewBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
