from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Index, CheckConstraint, UUID
from sqlalchemy.orm import relationship, validates
from datetime import datetime
import uuid
from app.models.base import Base


class Return(Base):
    __tablename__ = "returns"
    
    # Primary Key
    return_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Sale Reference
    sale_id = Column(UUID(as_uuid=True), ForeignKey('sales.sale_id'), nullable=False)
    sku = Column(String(50), ForeignKey('products.sku'), nullable=False)
    
    # Return Details
    qty = Column(Integer, nullable=False)
    reason = Column(String(200), nullable=False)  # Defective, Wrong Size, Changed Mind, etc.
    condition = Column(String(50), nullable=False)  # New, Good, Damaged
    restock = Column(Boolean, default=False, nullable=False)  # Whether to add back to inventory
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    sale = relationship("Sale", back_populates="returns")
    product = relationship("Product", back_populates="returns")
    
    # Indexes
    __table_args__ = (
        Index('idx_return_sale', 'sale_id'),
        Index('idx_return_sku', 'sku'),
        Index('idx_return_timestamp', 'timestamp'),
        Index('idx_return_restock', 'restock'),
        CheckConstraint('qty > 0', name='check_return_qty_positive'),
    )
    
    # Validators
    @validates('qty')
    def validate_qty(self, key, value):
        if value <= 0:
            raise ValueError("Return quantity must be greater than 0")
        return value
    
    @validates('condition')
    def validate_condition(self, key, value):
        valid_conditions = ['New', 'Good', 'Damaged', 'Defective']
        if value not in valid_conditions:
            raise ValueError(f"Condition must be one of {valid_conditions}")
        return value
    
    @validates('reason')
    def validate_reason(self, key, value):
        if not value or len(value.strip()) == 0:
            raise ValueError("Return reason cannot be empty")
        return value
    
    def __repr__(self):
        return f"<Return(id={self.return_id}, sale_id={self.sale_id}, sku='{self.sku}', qty={self.qty}, restock={self.restock})>"