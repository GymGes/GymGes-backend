from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from core.database import Base

class Plan(Base):
    __tablename__="plans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(120), nullable=False, index=True)
    credits = Column(Integer, nullable=False, index=True)

    member= relationship("Member", back_populates="record_label",cascade="all, delete-orphan")
    def __repr__(self) -> str:
        return f"<Plan (id={self.id}, name='{self.name}')>"