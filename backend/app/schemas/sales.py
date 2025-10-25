from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class SaleBase(BaseModel):
    sku: str
    quantity: int
    total_price: float
    sale_date: Optional[datetime] = None


class SaleCreate(SaleBase):
    """Schema for creating a new sale."""
    pass


class SaleUpdate(BaseModel):
    """Schema for updating an existing sale."""
    quantity: Optional[int] = None
    total_price: Optional[float] = None
    sale_date: Optional[datetime] = None


class SaleResponse(SaleBase):
    """Schema for returning sale data from API."""
    sale_id: UUID  # assuming your Sale model uses UUID primary key

    class Config:
        from_attributes = True  # enables ORM mode for SQLAlchemy models
