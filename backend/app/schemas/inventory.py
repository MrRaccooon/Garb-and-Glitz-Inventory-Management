from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class InventoryAdjust(BaseModel):
    """
    Request schema for adjusting inventory quantities.
    """
    sku: str
    quantity: int
    reason: Optional[str] = None

    class Config:
        from_attributes = True


class LedgerEntryResponse(BaseModel):
    """
    Response schema for individual inventory ledger entries.
    """
    id: int
    sku: str
    change: int
    reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InventoryResponse(BaseModel):
    """
    Response schema for current inventory status of a product.
    """
    sku: str
    quantity: int
    last_updated: datetime

    class Config:
        from_attributes = True
