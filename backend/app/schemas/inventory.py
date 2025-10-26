from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class InventoryAdjust(BaseModel):
    """
    Request schema for adjusting inventory quantities.
    """
    sku: str
    quantity: int
    reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class LedgerEntryResponse(BaseModel):
    """
    Response schema for individual inventory ledger entries.
    """
    transaction_id: str  # Changed from 'id' to match your model
    sku: str
    change_qty: int  # Changed from 'change'
    reason: Optional[str] = None
    timestamp: datetime  # Changed from 'created_at'

    model_config = ConfigDict(from_attributes=True)


class InventoryResponse(BaseModel):
    """
    Response schema for current inventory status of a product.
    """
    sku: str
    name: str  # ADDED - comes from query
    category: str  # ADDED - comes from query
    balance_qty: int  # CHANGED from 'quantity' to match query
    reorder_point: int  # ADDED - comes from query
    needs_reorder: bool  # ADDED - calculated field

    model_config = ConfigDict(from_attributes=True)


class LowStockItem(BaseModel):
    """
    Response schema for low stock alerts.
    """
    sku: str
    name: str
    current_stock: int
    reorder_point: int
    suggested_order_qty: int
    
    model_config = ConfigDict(from_attributes=True)