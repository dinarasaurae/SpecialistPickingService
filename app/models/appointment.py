from datetime import datetime
from typing import TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import Integer, ForeignKey, DateTime, DECIMAL, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base
from app.schemas.enums import AppointmentStatus

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.psychologist import Psychologist

class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    psychologist_id: Mapped[int] = mapped_column(ForeignKey("psychologists.id"))
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    price: Mapped[Decimal] = mapped_column(DECIMAL, nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus, native_enum=False), 
        nullable=False, 
        default=AppointmentStatus.pending
        )

    client: Mapped["User"] = relationship("User", back_populates="appointments")
    psychologist: Mapped["Psychologist"] = relationship("Psychologist") # здесь не нужен back_populates
