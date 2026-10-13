from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from core.database import Base


class ActivityType(Base):
    """
    SQLAlchemy ORM Model representing the 'activity_types' table.
    """
    __tablename__ = "activity_types"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), nullable=False, index=True, unique=True)
    duration = Column(Integer, nullable=False)
    max_students = Column(Integer, nullable=False)
    description = Column(String(255), nullable=True)
    weekly_classes = relationship(          
        "WeeklyClass",
        back_populates="activity_type",
        cascade="all, delete-orphan"
    )


    def __repr__(self) -> str:
        return f"<ActivityType(id={self.id}, name='{self.name}')>"
