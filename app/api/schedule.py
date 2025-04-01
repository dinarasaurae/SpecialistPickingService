from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleCreate, ScheduleRead

router = APIRouter(prefix="/schedule", tags=["Schedule"])

@router.post("/", response_model=ScheduleRead)
def create_schedule(schedule_data: ScheduleCreate, db: Session = Depends(get_db)):
    if schedule_data.day_of_week not in range(0, 7):
        raise HTTPException(status_code=400)
    new_schedule = Schedule(**schedule_data.model_dump())
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return new_schedule

@router.get("/{psychologist_id}", response_model=list[ScheduleRead])
def get_schedule(psychologist_id: int, db: Session = Depends(get_db)):
    schedule = db.query(Schedule).filter(Schedule.psychologist_id == psychologist_id).all()
    if not schedule:
        raise HTTPException(status_code=404, detail="Расписание не найдено")
    return schedule

@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Расписание не найдено")
    db.delete(schedule)
    db.commit()
    return {"message": "Расписание удалено"}
