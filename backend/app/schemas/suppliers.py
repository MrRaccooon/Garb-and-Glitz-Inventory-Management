"""
Pydantic schemas for supplier operations.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class SupplierBase(BaseModel):
    """Base schema for supplier information"""
    name: str = Field(..., min_length=1, max_length=200, description="Supplier name")
    contact: str = Field(..., min_length=10, max_length=15, description="Contact number")
    email: Optional[EmailStr] = Field(None, description="Email address")
    lead_time_days: int = Field(default=7, gt=0, description="Lead time in days")
    active: bool = Field(default=True, description="Whether supplier is active")


class SupplierCreate(SupplierBase):
    """Schema for creating a new supplier"""
    pass


class SupplierUpdate(BaseModel):
    """Schema for updating an existing supplier"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    contact: Optional[str] = Field(None, min_length=10, max_length=15)
    email: Optional[EmailStr] = None
    lead_time_days: Optional[int] = Field(None, gt=0)
    active: Optional[bool] = None


class SupplierResponse(SupplierBase):
    """Schema for supplier response"""
    supplier_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
