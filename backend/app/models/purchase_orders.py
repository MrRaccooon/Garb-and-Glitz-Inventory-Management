from sqlalchemy import Column, String, Integer, Numeric, DateTime, Date, ForeignKey, Index, CheckConstraint, UUID
from sqlalchemy.orm import relationship, validates
from datetime import datetime
import uuid
from app.models.base import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    
    # Primary Key
    po_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Supplier and Product
    supplier_id = Column(UUID(as_uuid=True), ForeignKey('suppliers.supplier_id'), nullable=False)
    sku = Column(String(50), ForeignKey('products.sku'), nullable=False)
    
    # Quantity Details
    qty_ordered = Column(Integer, nullable=False)
    qty_received = Column(Integer, default=0, nullable=False)
    
    # Date Information
    order_date = Column(Date, default=datetime.utcnow().date, nullable=False)
    expected_date = Column(Date, nullable=True)
    received_date = Column(Date, nullable=True)
    
    # Status and Pricing
    status = Column(String(20), default='Pending', nullable=False)  # Pending, Partial, Received, Cancelled
    unit_cost = Column(Numeric(10, 2), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="purchase_orders")
    product = relationship("Product", back_populates="purchase_orders")
    
    # Indexes
    __table_args__ = (
        Index('idx_po_supplier', 'supplier_id'),
        Index('idx_po_sku', 'sku'),
        Index('idx_po_status', 'status'),
        Index('idx_po_order_date', 'order_date'),
        Index('idx_po_expected_date', 'expected_date'),
        CheckConstraint('qty_ordered > 0', name='check_qty_ordered_positive'),
        CheckConstraint('qty_received >= 0', name='check_qty_received_non_negative'),
        CheckConstraint('qty_received <= qty_ordered', name='check_qty_received_lte_ordered'),
        CheckConstraint('unit_cost > 0', name='check_unit_cost_positive'),
        CheckConstraint('expected_date >= order_date', name='check_expected_after_order'),
        CheckConstraint('received_date >= order_date OR received_date IS NULL', name='check_received_after_order'),
    )
    
    # Validators
    @validates('qty_ordered')
    def validate_qty_ordered(self, key, value):
        if value <= 0:
            raise ValueError("Ordered quantity must be greater than 0")
        return value
    
    @validates('qty_received')
    def validate_qty_received(self, key, value):
        if value < 0:
            raise ValueError("Received quantity cannot be negative")
        if hasattr(self, 'qty_ordered') and value > self.qty_ordered:
            raise ValueError("Received quantity cannot exceed ordered quantity")
        return value
    
    @validates('unit_cost')
    def validate_unit_cost(self, key, value):
        if value <= 0:
            raise ValueError("Unit cost must be greater than 0")
        return value
    
    @validates('expected_date')
    def validate_expected_date(self, key, value):
        if value and hasattr(self, 'order_date') and value < self.order_date:
            raise ValueError("Expected date cannot be before order date")
        return value
    
    @validates('received_date')
    def validate_received_date(self, key, value):
        if value and hasattr(self, 'order_date') and value < self.order_date:
            raise ValueError("Received date cannot be before order date")
        return value
    
    @validates('status')
    def validate_status(self, key, value):
        valid_statuses = ['Pending', 'Partial', 'Received', 'Cancelled']
        if value not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        return value
    
    def __repr__(self):
        return f"<PurchaseOrder(id={self.po_id}, sku='{self.sku}', qty_ordered={self.qty_ordered}, qty_received={self.qty_received}, status='{self.status}')>"