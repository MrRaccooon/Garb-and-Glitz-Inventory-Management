from sqlalchemy import Column, String, Numeric, Integer, Boolean, DateTime, ForeignKey, Index, CheckConstraint, UUID
from sqlalchemy.orm import relationship, validates
from datetime import datetime
from app.models.base import Base


class Product(Base):
    __tablename__ = "products"
    
    # Primary Key
    sku = Column(String(50), primary_key=True)
    
    # Basic Information
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)  # saree, suit, lehenga
    subcategory = Column(String(50), nullable=True)  # Banarasi, Kanjivaram, Anarkali, etc.
    brand = Column(String(100), nullable=True)
    size = Column(String(20), nullable=True)  # Free Size, S, M, L, XL, XXL
    color = Column(String(50), nullable=False)
    fabric = Column(String(50), nullable=True)  # Silk, Cotton, Georgette, etc.
    
    # Pricing
    cost_price = Column(Numeric(10, 2), nullable=False)
    sell_price = Column(Numeric(10, 2), nullable=False)
    
    # Inventory Management
    reorder_point = Column(Integer, default=5, nullable=False)
    lead_time_days = Column(Integer, default=7, nullable=False)
    
    # Supplier Relationship
    supplier_id = Column(UUID(as_uuid=True), ForeignKey('suppliers.supplier_id'), nullable=False)
    
    # Additional Attributes
    season_tag = Column(String(50), nullable=True)  # Summer, Winter, Festive, Wedding
    hsn_code = Column(String(10), nullable=True)  # HSN code for GST
    active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="products")
    sales = relationship("Sale", back_populates="product")
    inventory_ledger = relationship("InventoryLedger", back_populates="product")
    purchase_orders = relationship("PurchaseOrder", back_populates="product")
    returns = relationship("Return", back_populates="product")
    
    # Indexes
    __table_args__ = (
        Index('idx_product_sku', 'sku'),
        Index('idx_product_category', 'category'),
        Index('idx_product_supplier', 'supplier_id'),
        Index('idx_product_active', 'active'),
        Index('idx_product_category_subcategory', 'category', 'subcategory'),
        CheckConstraint('cost_price > 0', name='check_cost_price_positive'),
        CheckConstraint('sell_price > 0', name='check_sell_price_positive'),
        CheckConstraint('reorder_point >= 0', name='check_reorder_point_non_negative'),
        CheckConstraint('lead_time_days > 0', name='check_lead_time_positive'),
    )
    
    # Validators
    @validates('cost_price', 'sell_price')
    def validate_price(self, key, value):
        if value <= 0:
            raise ValueError(f"{key} must be greater than 0")
        return value
    
    @validates('reorder_point')
    def validate_reorder_point(self, key, value):
        if value < 0:
            raise ValueError("Reorder point cannot be negative")
        return value
    
    @validates('lead_time_days')
    def validate_lead_time(self, key, value):
        if value <= 0:
            raise ValueError("Lead time must be greater than 0")
        return value
    
    def __repr__(self):
        return f"<Product(sku='{self.sku}', name='{self.name}', category='{self.category}', price={self.sell_price})>"