from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID  # ← ADD THIS IMPORT

class ProductBase(BaseModel):
    name: str
    category: str
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    size: Optional[str] = None
    color: str
    fabric: Optional[str] = None
    cost_price: float
    sell_price: float
    reorder_point: int = 5
    lead_time_days: int = 7
    supplier_id: UUID  # ← Now UUID is imported
    season_tag: Optional[str] = None
    hsn_code: Optional[str] = None
    active: bool = True

class ProductCreate(ProductBase):
    sku: str  # Add SKU for creation

class ProductUpdate(ProductBase):
    pass

class ProductResponse(ProductBase):
    sku: str
    created_at: datetime
    updated_at: datetime

    # Pydantic v2 syntax (replaces orm_mode = True)
    model_config = ConfigDict(from_attributes=True)