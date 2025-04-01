from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.psychologist import Psychologist

class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    psychologist_id: Mapped[int] = mapped_column(ForeignKey("psychologists.id"))
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    client: Mapped["User"] = relationship("User", back_populates="reviews")
    psychologist: Mapped["Psychologist"] = relationship("Psychologist", back_populates="reviews")
