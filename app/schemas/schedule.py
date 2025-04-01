from pydantic import BaseModel
from datetime import time

class ScheduleBase(BaseModel):
    psychologist_id: int
    day_of_week: int
    start_time: time
    end_time: time

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleRead(ScheduleBase):
    id: int

    class Config:
        from_attributes = True
