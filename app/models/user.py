from datetime import datetime, timezone
from typing import TYPE_CHECKING, List
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.chat import Chat
    from app.models.review import Review
    from app.models.psychologist import Psychologist
    from app.models.appointment import Appointment

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    psychologist: Mapped["Psychologist"] = relationship("Psychologist", back_populates="user", uselist=False)
    chats_sent: Mapped[List["Chat"]] = relationship("Chat", foreign_keys="[Chat.sender_id]", back_populates="sender")
    chats_received: Mapped[List["Chat"]] = relationship("Chat", foreign_keys="[Chat.receiver_id]", back_populates="receiver")
    appointments: Mapped[List["Appointment"]] = relationship("Appointment", back_populates="client")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="client")
