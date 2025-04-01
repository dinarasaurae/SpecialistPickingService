from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.models.psychologist import Psychologist
from app.models.specialization import Specialization
from app.schemas.psychologist import PsychologistCreate, PsychologistRead

router = APIRouter(prefix="/psychologists", tags=["Psychologists"])

@router.post("/", response_model=PsychologistRead)
def create_psychologist(psychologist_data: PsychologistCreate, db: Session = Depends(get_db)) -> PsychologistRead:

    new_psychologist = Psychologist(
        user_id=psychologist_data.user_id,
        experience=psychologist_data.experience,
        bio=psychologist_data.bio,
        price_per_hour=psychologist_data.price_per_hour
    )
    db.add(new_psychologist)
    db.commit()
    db.refresh(new_psychologist)
    if psychologist_data.specialization_ids:
        specializations = db.query(Specialization).filter(
            Specialization.id.in_(psychologist_data.specialization_ids)
        ).all()
        if not specializations:
            raise HTTPException(status_code=400, detail="какие-то специализации не найдены")
        
        new_psychologist.specializations.extend(specializations)
        db.commit()
    return new_psychologist

@router.get("/{psychologist_id}", response_model=PsychologistRead)
def get_psychologist(psychologist_id: int, db: Session = Depends(get_db)) -> PsychologistRead:
    psychologist = (
        db.query(Psychologist)
        .options(
            joinedload(Psychologist.user),
            joinedload(Psychologist.specializations),
            joinedload(Psychologist.schedule),
            joinedload(Psychologist.reviews),
        )
        .filter(Psychologist.id == psychologist_id)
        .first()
    )
    if not psychologist:
        raise HTTPException(status_code=404, detail="Психолог не найден")
    return psychologist

@router.put("/{psychologist_id}", response_model=PsychologistRead)
def update_psychologist(
    psychologist_id: int,
    psychologist_data: PsychologistCreate,
    db: Session = Depends(get_db)
):
    psychologist = db.query(Psychologist).filter(Psychologist.id == psychologist_id).first()
    if not psychologist:
        raise HTTPException(status_code=404, detail="Психолог не найден")

    psychologist.experience = psychologist_data.experience
    psychologist.bio = psychologist_data.bio
    psychologist.price_per_hour = psychologist_data.price_per_hour

    if psychologist_data.specialization_ids:
        specializations = db.query(Specialization).filter(
            Specialization.id.in_(psychologist_data.specialization_ids)
        ).all()
        if not specializations:
            raise HTTPException(status_code=400)
        
        psychologist.specializations = specializations  
    
    db.commit()
    db.refresh(psychologist)

    return psychologist
