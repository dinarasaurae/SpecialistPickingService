from sqlalchemy import ForeignKey, Integer, Table, Column
from sqlalchemy.orm import mapped_column
from app.core.database import Base

psychologist_specializations = Table(
    "psychologist_specializations",
    Base.metadata,
    Column("psychologist_id", Integer, ForeignKey("psychologists.id"), primary_key=True),
    Column("specialization_id", Integer, ForeignKey("specializations.id"), primary_key=True),
)