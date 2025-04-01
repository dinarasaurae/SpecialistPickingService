from pydantic import BaseModel, Field
from datetime import time
from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING
from app.schemas.user import UserRead
from app.schemas.schedule import ScheduleRead
from app.schemas.review import ReviewRead
from app.schemas.appointment import AppointmentRead

if TYPE_CHECKING:
    from app.schemas.specialization import SpecializationRead

class PsychologistBase(BaseModel):
    experience: int = Field(..., ge=0, description="Опыт работы в годах")
    bio: Optional[str] = Field(None, description="Краткая биография")
    price_per_hour: Optional[Decimal] = Field(None, description="Цена за час консультации")

class PsychologistCreate(PsychologistBase):
    user_id: int
    specialization_ids: List[int] = Field(default=[])

class PsychologistRead(PsychologistBase):
    id: int
    user: UserRead
    specializations: List["SpecializationRead"] = [] # строка!!!
    schedule: List[ScheduleRead] = []
    reviews: List[ReviewRead] = []
    rating: float

    class Config:
        from_attributes = True

from app.schemas.specialization import SpecializationRead  # Импорт ТОЛЬКО здесь!
PsychologistRead.model_rebuild()