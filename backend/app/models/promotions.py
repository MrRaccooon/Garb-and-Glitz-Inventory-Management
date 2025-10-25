from sqlalchemy import Column, String, Numeric, Date, Boolean, DateTime, Index, CheckConstraint, UUID
from sqlalchemy.orm import validates
from datetime import datetime
import uuid
from app.models.base import Base


class Promotion(Base):
    __tablename__ = "promotions"
    
    # Primary Key
    promo_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Promotion Details
    name = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    discount_pct = Column(Numeric(5, 2), nullable=False)  # Discount percentage (e.g., 15.50 for 15.5%)
    active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_promo_dates', 'start_date', 'end_date'),
        Index('idx_promo_active', 'active'),
        CheckConstraint('discount_pct > 0', name='check_discount_positive'),
        CheckConstraint('discount_pct <= 100', name='check_discount_max_100'),
        CheckConstraint('end_date >= start_date', name='check_end_after_start'),
    )
    
    # Validators
    @validates('discount_pct')
    def validate_discount(self, key, value):
        if value <= 0:
            raise ValueError("Discount percentage must be greater than 0")
        if value > 100:
            raise ValueError("Discount percentage cannot exceed 100")
        return value
    
    @validates('end_date')
    def validate_end_date(self, key, value):
        if hasattr(self, 'start_date') and value < self.start_date:
            raise ValueError("End date cannot be before start date")
        return value
    
    @validates('name')
    def validate_name(self, key, value):
        if not value or len(value.strip()) == 0:
            raise ValueError("Promotion name cannot be empty")
        return value
    
    def is_active_on_date(self, check_date):
        """Check if promotion is active on a specific date"""
        return self.active and self.start_date <= check_date <= self.end_date
    
    def __repr__(self):
        return f"<Promotion(id={self.promo_id}, name='{self.name}', discount={self.discount_pct}%, active={self.active})>"