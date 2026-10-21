from sqlalchemy import Column, Integer, String, ForeignKey, event, select, update
from sqlalchemy.orm import relationship

from core.config import now_local
from core.database import Base
from models.member_model import Member
from models.weekly_class_model import WeeklyClass

class Booking(Base):
    
    __tablename__ = "booking"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    member_code = Column(String(9), ForeignKey("members.code"), nullable=False, index=True)
    class_id = Column(Integer, ForeignKey("weekly_classes.id"), nullable=False, index=True)
    
    member = relationship("Member", back_populates="bookings")
    weekly_class = relationship("WeeklyClass", back_populates="bookings")


    def __repr__(self) -> str:
        return f"<Booking(id={self.id}, member_code={self.member_code}, class_id={self.class_id})>"


@event.listens_for(Booking, "before_delete")
def _refund_credit_on_cascade_delete(mapper, connection, target: Booking) -> None:
    activity_date = connection.execute(
        select(WeeklyClass.activity_date).where(WeeklyClass.id == target.class_id)
    ).scalar_one_or_none()

    if activity_date is None or activity_date <= now_local():
        return

    connection.execute(
        update(Member)
        .where(Member.code == target.member_code)
        .values(remaining_credits=Member.remaining_credits + 1)
    )


