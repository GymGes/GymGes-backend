from sqlalchemy import Column, Integer, String, DateTime
from core.database import Base

class Booking(Base):
    
    __tablename__ = "booking"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    member_code = Column(String(50), nullable=False, index=True)
    class_id = Column(Integer, nullable=False, index=True)
    booking_date = Column(DateTime, nullable=False)
    
    def __repr__(self) -> str:
        return f"<Booking(id={self.id}, member_code={self.member_code}, class_id={self.class_id})>"