from pydantic import BaseModel
from typing import List
from datetime import date


class ForecastItem(BaseModel):
    sku: str
    predicted_quantity: int
    date: date

    class Config:
        from_attributes = True


class ForecastRequest(BaseModel):
    start_date: date
    end_date: date
    skus: List[str]

    class Config:
        from_attributes = True


class ForecastDataPoint(BaseModel):
    """
    Represents a single data point in a forecast response with confidence intervals
    """
    date: date
    value: float  # Primary forecast value
    lower_bound: float  # Lower confidence interval
    upper_bound: float  # Upper confidence interval

    class Config:
        from_attributes = True


class ForecastResponse(BaseModel):
    sku: str
    product_name: str
    forecast_horizon_days: int
    forecast: List[ForecastDataPoint]
    historical_avg_daily_sales: float
    confidence_level: float

    class Config:
        from_attributes = True
