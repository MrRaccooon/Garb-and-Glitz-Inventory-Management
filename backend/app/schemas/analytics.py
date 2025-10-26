from pydantic import BaseModel, ConfigDict
from typing import List
from datetime import date

class TopProductResponse(BaseModel):
    sku: str
    name: str
    category: str
    total_revenue: float
    total_quantity: int
    transaction_count: int
    avg_transaction_value: float

    model_config = ConfigDict(from_attributes=True)

class RevenueTrendResponse(BaseModel):
    date: date
    revenue: float
    units_sold: int
    transaction_count: int
    avg_order_value: float

    model_config = ConfigDict(from_attributes=True)

class CategoryBreakdownResponse(BaseModel):
    category: str
    revenue: float
    quantity: int
    unique_products: int
    transaction_count: int
    revenue_percentage: float

    model_config = ConfigDict(from_attributes=True)

class ABCAnalysisResponse(BaseModel):
    sku: str
    name: str
    category: str
    revenue: float
    quantity: int
    revenue_percentage: float
    cumulative_revenue_percentage: float
    abc_classification: str

    model_config = ConfigDict(from_attributes=True)