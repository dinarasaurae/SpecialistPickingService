from pydantic import BaseModel, Field
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.psychologist import PsychologistRead  # Импорт ТОЛЬКО для аннотаций

class SpecializationBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Название специализации")
    description: Optional[str] = Field(None, description="Описание специализации")

class SpecializationCreate(SpecializationBase):
    pass

class SpecializationRead(SpecializationBase):
    id: int
    psychologists: List["PsychologistRead"] = []  

    class Config:
        from_attributes = True

from app.schemas.psychologist import PsychologistRead  
SpecializationRead.model_rebuild()  
