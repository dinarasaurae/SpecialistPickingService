from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Any
from decimal import Decimal
from app.schemas.enums import AppointmentStatus

class AppointmentBase(BaseModel):
    client_id: int
    psychologist_id: int
    start_time: datetime
    end_time: datetime
    price: Decimal = Field(..., gt=0)

    @field_validator("start_time", mode="before")
    @classmethod
    def validate_start_time(cls, value: datetime) -> datetime:
        if value <= datetime.now(timezone.utc):
            raise ValueError("Время начала должно быть в будущем")
        return value

    @field_validator("end_time", mode="before")
    @classmethod
    def validate_end_time(cls, value: datetime, values: dict[str, Any]) -> datetime:
        start_time = values.get("start_time")
        if start_time and value <= start_time:
            raise ValueError("время окончания должно быть позже начала")
        return value

class AppointmentCreate(AppointmentBase):
    status: AppointmentStatus = Field(default=AppointmentStatus.pending, description="Статус записи")

class AppointmentRead(AppointmentBase):
    id: int
    status: AppointmentStatus

    class Config:
        from_attributes = True
