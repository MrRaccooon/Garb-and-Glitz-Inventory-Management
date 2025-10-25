from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Index, CheckConstraint, UUID
from sqlalchemy.orm import relationship, validates
from datetime import datetime
import uuid
from app.models.base import Base


class Sale(Base):
    __tablename__ = "sales"
    
    # Primary Key
    sale_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Transaction Details
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    sku = Column(String(50), ForeignKey('products.sku'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    discount = Column(Numeric(10, 2), default=0.0, nullable=False)
    gst_amount = Column(Numeric(10, 2), default=0.0, nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    
    # Payment Information
    payment_mode = Column(String(20), nullable=False)  # Cash, Card, UPI, NetBanking
    invoice_number = Column(String(50), unique=True, nullable=False)
    customer_phone = Column(String(15), nullable=True)
    
    # Relationships
    product = relationship("Product", back_populates="sales")
    returns = relationship("Return", back_populates="sale")
    
    # Indexes
    __table_args__ = (
        Index('idx_sale_timestamp', 'timestamp'),
        Index('idx_sale_sku', 'sku'),
        Index('idx_sale_invoice', 'invoice_number'),
        Index('idx_sale_customer', 'customer_phone'),
        Index('idx_sale_date_sku', 'timestamp', 'sku'),
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
        CheckConstraint('unit_price > 0', name='check_unit_price_positive'),
        CheckConstraint('discount >= 0', name='check_discount_non_negative'),
        CheckConstraint('gst_amount >= 0', name='check_gst_non_negative'),
        CheckConstraint('total > 0', name='check_total_positive'),
    )
    
    # Validators
    @validates('quantity')
    def validate_quantity(self, key, value):
        if value <= 0:
            raise ValueError("Quantity must be greater than 0")
        return value
    
    @validates('unit_price', 'total')
    def validate_price(self, key, value):
        if value <= 0:
            raise ValueError(f"{key} must be greater than 0")
        return value
    
    @validates('discount', 'gst_amount')
    def validate_non_negative(self, key, value):
        if value < 0:
            raise ValueError(f"{key} cannot be negative")
        return value
    
    @validates('payment_mode')
    def validate_payment_mode(self, key, value):
        valid_modes = ['Cash', 'Card', 'UPI', 'NetBanking', 'Wallet']
        if value not in valid_modes:
            raise ValueError(f"Payment mode must be one of {valid_modes}")
        return value
    
    def __repr__(self):
        return f"<Sale(id={self.sale_id}, invoice='{self.invoice_number}', sku='{self.sku}', qty={self.quantity}, total={self.total})>"