from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from core.database import Base

class Teacher(Base):
    __tablename__="teachers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(120), nullable=False, index=True)

    weeklyClass= relationship("WeeklyClass", back_populates="record_label",cascade="all, delete-orphan")
    def __repr__(self) -> str:
        return f"<Teacher (id={self.id}, name='{self.name}')>"