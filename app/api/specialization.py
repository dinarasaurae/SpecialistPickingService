from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.models.specialization import Specialization
from app.schemas.specialization import SpecializationBase, SpecializationRead

router = APIRouter(prefix="/specializations", tags=["Specializations"])

@router.post("/", response_model=SpecializationRead)
def create_specialization(specialization_data: SpecializationBase, db: Session = Depends(get_db)):
    new_specialization = Specialization(**specialization_data.model_dump())
    db.add(new_specialization)
    db.commit()
    db.refresh(new_specialization)
    return new_specialization

@router.get("/{specialization_id}", response_model=SpecializationRead)
def get_specialization(specialization_id: int, db: Session = Depends(get_db)):
    specialization = (
        db.query(Specialization)
        .options(joinedload(Specialization.psychologists))
        .filter(Specialization.id == specialization_id)
        .first()
    )
    if not specialization:
        raise HTTPException(status_code=404, detail="Специализация не найдена")
    return specialization
