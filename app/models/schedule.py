from typing import TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, Time
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.psychologist import Psychologist

class Schedule(Base):
    __tablename__ = "schedule"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    psychologist_id: Mapped[int] = mapped_column(ForeignKey("psychologists.id"))
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[Time] = mapped_column(Time, nullable=False)
    end_time: Mapped[Time] = mapped_column(Time, nullable=False)

    psychologist: Mapped["Psychologist"] = relationship("Psychologist", back_populates="schedule")
