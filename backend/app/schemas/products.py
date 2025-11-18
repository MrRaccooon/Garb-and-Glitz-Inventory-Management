"""
Product Pydantic Schemas - FIXED VERSION
File: backend/app/schemas/products.py
"""
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID


class ProductBase(BaseModel):
    """Base product fields - used for creation"""
    name: str
    category: str
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    fabric: Optional[str] = None
    cost_price: float
    sell_price: float
    reorder_point: int = 10
    lead_time_days: int = 7
    supplier_id: Optional[UUID] = None  # ✅ ADDED: Optional supplier
    season_tag: Optional[str] = None
    hsn_code: Optional[str] = None
    active: bool = True

    @field_validator('cost_price', 'sell_price')
    @classmethod
    def validate_prices(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return v

    @field_validator('reorder_point', 'lead_time_days')
    @classmethod
    def validate_positive_integers(cls, v):
        if v < 0:
            raise ValueError('Must be a non-negative integer')
        return v


class ProductCreate(ProductBase):
    """Schema for creating a new product"""
    sku: str

    @field_validator('sku')
    @classmethod
    def validate_sku(cls, v):
        if not v or len(v) != 6:
            raise ValueError('SKU must be exactly 6 characters')
        if not (v[:3].isalpha() and v[:3].isupper() and v[3:].isdigit()):
            raise ValueError('SKU must be 3 uppercase letters followed by 3 digits (e.g., SAR001)')
        return v.upper()


class ProductUpdate(BaseModel):
    """
    Schema for updating products - ALL fields optional.
    """
    name: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    fabric: Optional[str] = None
    cost_price: Optional[float] = None
    sell_price: Optional[float] = None
    reorder_point: Optional[int] = None
    lead_time_days: Optional[int] = None
    supplier_id: Optional[UUID] = None  # ✅ ADDED: Optional supplier
    season_tag: Optional[str] = None
    hsn_code: Optional[str] = None
    active: Optional[bool] = None

    @field_validator('cost_price', 'sell_price')
    @classmethod
    def validate_prices(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be greater than 0')
        return v

    @field_validator('reorder_point', 'lead_time_days')
    @classmethod
    def validate_positive_integers(cls, v):
        if v is not None and v < 0:
            raise ValueError('Must be a non-negative integer')
        return v


class ProductResponse(ProductBase):
    """Schema for product responses"""
    sku: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)