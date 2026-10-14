from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from core.database import Base
from models.member_model import Member
from models.weekly_class_model import WeeklyClass

class Booking(Base):
    
    __tablename__ = "booking"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    member_code = Column(String(9), ForeignKey("member.code"), nullable=False, index=True)
    class_id = Column(Integer, ForeignKey("weekly_class.id"), nullable=False, index=True)
    booking_date = Column(DateTime, nullable=False)
    
    member = relationship("Member", back_populates="bookings")
    weekly_class = relationship("WeeklyClass", back_populates="bookings")


    def __repr__(self) -> str:
        return f"<Booking(id={self.id}, member_code={self.member_code}, class_id={self.class_id})>"


