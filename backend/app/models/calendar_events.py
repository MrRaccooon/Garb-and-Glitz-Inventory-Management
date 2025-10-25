from sqlalchemy import Column, String, Date, DateTime, Index, UUID, Enum
from sqlalchemy.orm import validates
from datetime import datetime
import uuid
import enum
from app.models.base import Base


class EventType(enum.Enum):
    HOLIDAY = "holiday"
    FESTIVAL = "festival"
    SALE = "sale"

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    
    # Primary Key
    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Event Details
    date = Column(Date, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    type = Column(Enum(EventType), nullable=False)
    region = Column(String(100), nullable=True)  # All India, North, South, East, West, specific states
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_event_date', 'date'),
        Index('idx_event_type', 'type'),
        Index('idx_event_region', 'region'),
        Index('idx_event_date_type', 'date', 'type'),
    )
    
    # Validators
    @validates('name')
    def validate_name(self, key, value):
        if not value or len(value.strip()) == 0:
            raise ValueError("Event name cannot be empty")
        return value
    
    @validates('date')
    def validate_date(self, key, value):
        if not value:
            raise ValueError("Event date is required")
        return value
    
    def __repr__(self):
        return f"<CalendarEvent(id={self.event_id}, name='{self.name}', date={self.date}, type='{self.type.value}')>"