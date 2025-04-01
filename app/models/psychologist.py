from typing import List, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import Integer, ForeignKey, String, Float, DECIMAL
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property
from app.core.database import Base
from app.models.psychologist_specialization import psychologist_specializations

if TYPE_CHECKING:
    from app.models.specialization import Specialization
    from app.models.schedule import Schedule
    from app.models.review import Review
    from app.models.user import User

class Psychologist(Base):
    __tablename__ = "psychologists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    experience: Mapped[int] = mapped_column(Integer, nullable=False)
    bio: Mapped[str | None] = mapped_column(String, nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_per_hour: Mapped[Decimal | None] = mapped_column(DECIMAL, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="psychologist", uselist=False)
    specializations: Mapped[List["Specialization"]] = relationship(
        "Specialization", secondary="psychologist_specializations", back_populates="psychologists"
    )
    schedule: Mapped[List["Schedule"]] = relationship("Schedule", back_populates="psychologist")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="psychologist")

    @hybrid_property
    def rating(self) -> float:
        if not self.reviews:
            return 0.0
        return sum(review.rating for review in self.reviews) / len(self.reviews)