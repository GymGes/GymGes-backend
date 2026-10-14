from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class Member(Base):
    __tablename__ = "members"

    code = Column(String(9), primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    city = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)

    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False, index=True)

    remaining_credits = Column(Integer, nullable=False)

    bookings = relationship("Booking", back_populates="member")
    plan = relationship("Plan", back_populates="member")