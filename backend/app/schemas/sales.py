from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class SaleBase(BaseModel):
    sku: str
    quantity: int
    unit_price: Decimal
    payment_mode: str


class SaleCreate(SaleBase):
    """Schema for creating a new sale."""
    pass


class SaleUpdate(BaseModel):
    """Schema for updating an existing sale."""
    quantity: Optional[int] = None
    unit_price: Optional[Decimal] = None
    payment_mode: Optional[str] = None


class SaleResponse(BaseModel):
    """Schema for returning sale data from API."""
    sale_id: UUID
    timestamp: datetime
    sku: str
    quantity: int
    unit_price: float
    discount:   float
    gst_amount: float
    total: float
    payment_mode: str
    invoice_number: str
    customer_phone: Optional[str] = None

    class Config:
        from_attributes = True