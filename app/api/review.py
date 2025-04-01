from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from app.core.database import get_db
from app.models.review import Review
from app.schemas.review import ReviewBase, ReviewRead

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/", response_model=ReviewRead)
def create_review(review_data: ReviewBase, db: Session = Depends(get_db)) -> ReviewRead:
    new_review = Review(**review_data.model_dump(), created_at=datetime.utcnow())
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

@router.get("/{psychologist_id}", response_model=list[ReviewRead])
def get_reviews(psychologist_id: int, db: Session = Depends(get_db)) ->  List[ReviewRead]:
    reviews = db.query(Review).filter(Review.psychologist_id == psychologist_id).all()
    if not reviews:
        raise HTTPException(status_code=404, detail="Отзывы не найдены")
    return reviews
