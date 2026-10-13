from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class WeeklyClass(Base):
    __tablename__= "weekly_classes"
    teacher_id = Column (Integer, ForeignKey("teachers.id"), primary_key=True)
    activity_type_id = Column (Integer, ForeignKey("activity_types.id"), primary_key=True)
    activity_date= Column(Date,nullable=False )

    teacher= relationship("Teacher", back_populates="weekly_classes")
    activity_type= relationship("ActivityType", back_populates="weekly_classes")
    def __repr__(self) -> str:
        return f"<Weekly activity (id_activity_type={self.activity_type_id}, teacher_id='{self.teacher_id}')>"