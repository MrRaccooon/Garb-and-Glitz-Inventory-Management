from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):twnenteneszt
    name: str
    category: str
    subcategory: Optional[str]
    brand: Optional[str]
    size: Optional[str]
    color: str
    fabric: Optional[str]
    cost_price: float
    sell_price: float
    reorder_point: int = 5
    lead_time_days: int = 7
    supplier_id: str
    season_tag: Optional[str]
    hsn_code: Optional[str]
    active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductResponse(ProductBase):
    sku: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
mvnhvhvmn