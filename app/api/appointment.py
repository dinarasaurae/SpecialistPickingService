from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.appointment import Appointment
from app.models.user import User
from app.models.psychologist import Psychologist
from app.schemas.appointment import AppointmentCreate, AppointmentRead
from app.schemas.enums import AppointmentStatus
from app.core.security import get_current_user

router = APIRouter(prefix="/appointments", tags=["Appointments"])

# только клиент 
@router.post("/", response_model=AppointmentRead)
def create_appointment(
    appointment_data: AppointmentCreate, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
) -> AppointmentRead:
    
    # проверка на существование психолога
    psychologist = db.query(Psychologist).filter(Psychologist.id == appointment_data.psychologist_id).first()
    if not psychologist:
        raise HTTPException(status_code=404, detail="Психолог не найден")

    # Создаём запись
    new_appointment = Appointment(
        client_id=user.id,  # Берём ID текущего клиента
        psychologist_id=appointment_data.psychologist_id,
        start_time=appointment_data.start_time,
        end_time=appointment_data.end_time,
        price=appointment_data.price,
        status=AppointmentStatus.pending  # По умолчанию "ожидание"
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return AppointmentRead.model_validate(new_appointment)

# получение одной записи (клиент или психолог)
@router.get("/{appointment_id}", response_model=AppointmentRead)
def get_appointment(
    appointment_id: int, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
) -> AppointmentRead:
    """Клиент или психолог могут получить только свои записи"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    # Проверяем доступ (или клиент, или психолог)
    if appointment.client_id != user.id and (not user.psychologist or appointment.psychologist_id != user.psychologist.id):
        raise HTTPException(status_code=403, detail="Нет доступа к этой записи")

    return AppointmentRead.model_validate(appointment)

# Обновление статуса записи (только психолог)
@router.patch("/{appointment_id}/status", response_model=AppointmentRead)
def update_appointment_status(
    appointment_id: int, 
    status: AppointmentStatus, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
)-> AppointmentRead:
    """Психолог меняет статус записи"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    # является ли пользователь психологом
    if not user.psychologist or appointment.psychologist_id != user.psychologist.id:
        raise HTTPException(status_code=403, detail="Вы не можете менять статус этой записи")

    appointment.status = status
    db.commit()
    db.refresh(appointment)
    return AppointmentRead.model_validate(appointment)

### Удаление записи (только клиент или психолог)
@router.delete("/{appointment_id}")
def delete_appointment(
    appointment_id: int, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Клиент может отменить запись, психолог может удалить запись"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    # Только клиент или психолог может удалить запись
    if appointment.client_id != user.id and (not user.psychologist or appointment.psychologist_id != user.psychologist.id):
        raise HTTPException(status_code=403, detail="Вы не можете удалить эту запись")

    db.delete(appointment)
    db.commit()
    return {"message": "Запись успешно удалена"}
