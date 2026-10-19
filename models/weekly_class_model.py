from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base


class WeeklyClass(Base):
    __tablename__ = "weekly_classes"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)
    activity_type_id = Column(Integer, ForeignKey("activity_types.id", ondelete="CASCADE"), nullable=False)
    activity_date = Column(DateTime, nullable=False)      
    available_spots = Column(Integer, nullable=False)     
    teacher = relationship("Teacher", back_populates="weekly_classes")
    activity_type = relationship("ActivityType", back_populates="weekly_classes")
    bookings = relationship("Booking", back_populates="weekly_class", cascade="all, delete-orphan")