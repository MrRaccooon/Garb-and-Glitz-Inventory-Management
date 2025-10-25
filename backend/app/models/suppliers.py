from sqlalchemy import Column, String, Integer, Boolean, DateTime, UUID, Index, CheckConstraint
from sqlalchemy.orm import relationship, validates
from datetime import datetime
import uuid
from app.models.base import Base


class Supplier(Base):
    __tablename__ = "suppliers"
    
    # Primary Key
    supplier_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic Information
    name = Column(String(200), nullable=False)
    contact = Column(String(15), nullable=False)
    email = Column(String(100), nullable=True)
    lead_time_days = Column(Integer, nullable=False, default=7)
    active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    products = relationship("Product", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
    
    # Indexes
    __table_args__ = (
        Index('idx_supplier_active', 'active'),
        Index('idx_supplier_name', 'name'),
        CheckConstraint('lead_time_days > 0', name='check_lead_time_positive'),
    )
    
    # Validators
    @validates('lead_time_days')
    def validate_lead_time(self, key, value):
        if value <= 0:
            raise ValueError("Lead time must be greater than 0")
        return value
    
    @validates('contact')
    def validate_contact(self, key, value):
        if not value or len(value) < 10:
            raise ValueError("Contact number must be at least 10 digits")
        return value
    
    @validates('email')
    def validate_email(self, key, value):
        if value and '@' not in value:
            raise ValueError("Invalid email format")
        return value
    
    def __repr__(self):
        return f"<Supplier(id={self.supplier_id}, name='{self.name}', active={self.active})>"