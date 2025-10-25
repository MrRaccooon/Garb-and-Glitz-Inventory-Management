from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index, CheckConstraint, UUID, Enum
from sqlalchemy.orm import relationship, validates
from datetime import datetime
import uuid
import enum
from app.models.base import Base


class TransactionReason(enum.Enum):
    SALE = "sale"
    PURCHASE = "purchase"
    RETURN = "return"
    ADJUST = "adjust"

class InventoryLedger(Base):
    __tablename__ = "inventory_ledger"
    
    # Primary Key
    transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Transaction Details
    sku = Column(String(50), ForeignKey('products.sku'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    change_qty = Column(Integer, nullable=False)  # Positive for additions, negative for deductions
    balance_qty = Column(Integer, nullable=False)  # Running balance after this transaction
    reason = Column(Enum(TransactionReason), nullable=False)
    reference_id = Column(String(100), nullable=True)  # Reference to sale_id, po_id, return_id, etc.
    
    # Relationships
    product = relationship("Product", back_populates="inventory_ledger")
    
    # Indexes
    __table_args__ = (
        Index('idx_ledger_sku', 'sku'),
        Index('idx_ledger_timestamp', 'timestamp'),
        Index('idx_ledger_sku_timestamp', 'sku', 'timestamp'),
        Index('idx_ledger_reason', 'reason'),
        CheckConstraint('balance_qty >= 0', name='check_balance_non_negative'),
    )
    
    # Validators
    @validates('balance_qty')
    def validate_balance(self, key, value):
        if value < 0:
            raise ValueError("Balance quantity cannot be negative")
        return value
    
    @validates('change_qty')
    def validate_change(self, key, value):
        if value == 0:
            raise ValueError("Change quantity cannot be zero")
        return value
    
    def __repr__(self):
        return f"<InventoryLedger(id={self.transaction_id}, sku='{self.sku}', change={self.change_qty}, balance={self.balance_qty}, reason='{self.reason.value}')>"