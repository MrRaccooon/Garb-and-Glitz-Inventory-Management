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
    Represents a single data point in a forecast response
    """
    date: date
    predicted_quantity: int

    class Config:
        from_attributes = True


class ForecastResponse(BaseModel):
    sku: str
    forecast: List[ForecastDataPoint]

    class Config:
        from_attributes = True
