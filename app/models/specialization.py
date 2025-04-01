from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base
from app.models.psychologist_specialization import psychologist_specializations

if TYPE_CHECKING:
    from app.models.psychologist import Psychologist

class Specialization(Base):
    __tablename__ = "specializations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    psychologists: Mapped[List["Psychologist"]] = relationship(
        "Psychologist",
        secondary=psychologist_specializations,
        back_populates="specializations",
    )
