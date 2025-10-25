"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, validator, constr, confloat, conint
from typing import Optional, List, Literal
from datetime import datetime, date
from decimal import Decimal


# ============================================================================
# Product Schemas
# ============================================================================

class ProductBase(BaseModel):
    """Base product schema with common fields."""
    name: constr(min_length=1, max_length=200) = Field(..., description="Product name")
    category: constr(min_length=1, max_length=100) = Field(..., description="Product category")
    cost_price: confloat(gt=0) = Field(..., description="Cost price per unit")
    sell_price: confloat(gt=0) = Field(..., description="Selling price per unit")
    reorder_point: conint(ge=0) = Field(..., description="Minimum stock level before reorder")
    lead_time_days: conint(ge=0) = Field(..., description="Lead time in days for restocking")
    supplier_id: Optional[int] = Field(None, description="Supplier identifier")


class ProductCreate(ProductBase):
    """Schema for creating a new product."""
    sku: constr(min_length=1, max_length=50) = Field(..., description="Stock Keeping Unit (unique)")
    
    @validator('sell_price')
    def validate_sell_price(cls, v, values):
        """Ensure sell price is greater than or equal to cost price."""
        if 'cost_price' in values and v < values['cost_price']:
            raise ValueError("Sell price must be greater than or equal to cost price")
        return v


class ProductUpdate(BaseModel):
    """Schema for updating an existing product."""
    name: Optional[constr(min_length=1, max_length=200)] = None
    category: Optional[constr(min_length=1, max_length=100)] = None
    cost_price: Optional[confloat(gt=0)] = None
    sell_price: Optional[confloat(gt=0)] = None
    reorder_point: Optional[conint(ge=0)] = None
    lead_time_days: Optional[conint(ge=0)] = None
    supplier_id: Optional[int] = None
    active: Optional[bool] = None
    
    class Config:
        extra = "forbid"  # Prevent extra fields


class ProductResponse(ProductBase):
    """Schema for product responses."""
    sku: str
    active: bool
    
    class Config:
        from_attributes = True


# ============================================================================
# Sale Schemas
# ============================================================================

class SaleCreate(BaseModel):
    """Schema for creating a sale."""
    sku: constr(min_length=1, max_length=50) = Field(..., description="Product SKU")
    quantity: conint(gt=0) = Field(..., description="Quantity sold")
    unit_price: confloat(gt=0) = Field(..., description="Unit price at time of sale")
    payment_mode: constr(min_length=1, max_length=50) = Field(..., description="Payment method")


class SaleResponse(BaseModel):
    """Schema for sale responses."""
    sale_id: int
    timestamp: datetime
    sku: str
    quantity: int
    unit_price: float
    total: float
    payment_mode: str
    
    class Config:
        from_attributes = True


# ============================================================================
# Inventory Schemas
# ============================================================================

class InventoryAdjust(BaseModel):
    """Schema for manual inventory adjustments."""
    sku: constr(min_length=1, max_length=50) = Field(..., description="Product SKU")
    change_qty: int = Field(..., description="Quantity change (positive or negative)")
    reason: constr(min_length=1, max_length=500) = Field(..., description="Reason for adjustment")
    
    @validator('reason')
    def validate_reason(cls, v):
        """Ensure reason is meaningful."""
        if len(v.strip()) < 5:
            raise ValueError("Reason must be at least 5 characters")
        return v.strip()


class InventoryResponse(BaseModel):
    """Schema for current inventory status."""
    sku: str
    name: str
    category: str
    balance_qty: int = Field(..., description="Current stock quantity")
    reorder_point: int
    needs_reorder: bool = Field(..., description="True if balance is below reorder point")


class LedgerEntryResponse(BaseModel):
    """Schema for inventory ledger entries."""
    transaction_id: int
    sku: str
    change_qty: int
    balance_qty: int
    reason: str
    timestamp: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Forecasting Schemas
# ============================================================================

class ForecastDataPoint(BaseModel):
    """Schema for a single forecast data point."""
    date: date = Field(..., description="Forecast date")
    value: float = Field(..., description="Forecasted demand")
    lower_bound: float = Field(..., description="Lower confidence interval")
    upper_bound: float = Field(..., description="Upper confidence interval")


class ForecastResponse(BaseModel):
    """Schema for forecast response."""
    sku: str
    product_name: str
    forecast_horizon_days: int
    forecast: List[ForecastDataPoint]
    historical_avg_daily_sales: float
    confidence_level: float = Field(0.95, description="Confidence level for intervals")


# ============================================================================
# Analytics Schemas
# ============================================================================

class TopProductResponse(BaseModel):
    """Schema for top product analytics."""
    sku: str
    name: str
    category: str
    total_revenue: float
    total_quantity: int
    transaction_count: int
    avg_transaction_value: float


class RevenueTrendResponse(BaseModel):
    """Schema for revenue trend data."""
    date: date
    revenue: float
    units_sold: int
    transaction_count: int
    avg_order_value: float


class CategoryBreakdownResponse(BaseModel):
    """Schema for category breakdown analytics."""
    category: str
    revenue: float
    quantity: int
    unique_products: int
    transaction_count: int
    revenue_percentage: float = Field(..., description="Percentage of total revenue")


class ABCAnalysisResponse(BaseModel):
    """Schema for ABC analysis results."""
    sku: str
    name: str
    category: str
    revenue: float
    quantity: int
    revenue_percentage: float
    cumulative_revenue_percentage: float
    abc_classification: Literal["A", "B", "C"] = Field(..., description="ABC classification")


# ============================================================================
# Common/Utility Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str
    error_code: Optional[str] = None


class SuccessResponse(BaseModel):
    """Schema for generic success responses."""
    message: str
    data: Optional[dict] = None


class PaginationMeta(BaseModel):
    """Schema for pagination metadata."""
    total: int
    skip: int
    limit: int
    has_more: bool


class BulkOperationResponse(BaseModel):
    """Schema for bulk operation results."""
    total_rows: int
    success: int
    failed: int
    errors: List[str] = Field(default_factory=list)