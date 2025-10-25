"""
Demand forecasting API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timedelta
import numpy as np

from app.dependencies import get_db
from app.schemas import ForecastResponse, ForecastDataPoint
from app.models import Sale, Product

router = APIRouter()


def calculate_forecast(sales_data: list, horizon_days: int) -> list[ForecastDataPoint]:
    """
    Calculate demand forecast using exponential smoothing.
    
    Args:
        sales_data: Historical sales data [(date, quantity), ...]
        horizon_days: Number of days to forecast
        
    Returns:
        list[ForecastDataPoint]: Forecasted values with confidence intervals
    """
    if not sales_data:
        return []
    
    # Extract quantities
    quantities = [qty for _, qty in sales_data]
    
    # Simple exponential smoothing
    alpha = 0.3  # Smoothing parameter
    
    # Calculate baseline (average)
    baseline = np.mean(quantities)
    
    # Calculate standard deviation for confidence intervals
    std_dev = np.std(quantities) if len(quantities) > 1 else baseline * 0.2
    
    # Generate forecast
    forecast = []
    current_date = sales_data[-1][0] if sales_data else datetime.now().date()
    
    # Use last observed value or baseline as starting point
    last_value = quantities[-1] if quantities else baseline
    smoothed_value = last_value
    
    for day in range(1, horizon_days + 1):
        forecast_date = current_date + timedelta(days=day)
        
        # Apply exponential smoothing (trend-adjusted)
        if len(quantities) > 1:
            trend = (quantities[-1] - quantities[0]) / len(quantities)
            smoothed_value = alpha * last_value + (1 - alpha) * (smoothed_value + trend)
        else:
            smoothed_value = baseline
        
        # Calculate confidence intervals (95%)
        margin = 1.96 * std_dev * np.sqrt(day)
        
        forecast.append(ForecastDataPoint(
            date=forecast_date,
            value=round(max(0, smoothed_value), 2),
            lower_bound=round(max(0, smoothed_value - margin), 2),
            upper_bound=round(smoothed_value + margin, 2)
        ))
    
    return forecast


@router.get("/forecast", response_model=ForecastResponse)
async def get_demand_forecast(
    sku: str = Query(..., description="Product SKU to forecast"),
    horizon: str = Query("4w", regex="^[1-9][0-9]*[wd]$", description="Forecast horizon (e.g., '4w', '30d')"),
    db: Session = Depends(get_db)
) -> ForecastResponse:
    """
    Generate demand forecast for a product.
    
    This endpoint analyzes historical sales data and produces a forecast
    using exponential smoothing. The forecast includes point estimates
    and 95% confidence intervals.
    
    Args:
        sku: Product SKU to forecast
        horizon: Forecast horizon (format: <number><w|d>, e.g., '4w' or '30d')
        db: Database session dependency
        
    Returns:
        ForecastResponse: Forecast data with confidence intervals
        
    Raises:
        HTTPException: 404 if product not found, 400 for invalid parameters
    """
    # Verify product exists
    product = db.query(Product).filter(Product.sku == sku).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU '{sku}' not found"
        )
    
    # Parse horizon
    unit = horizon[-1]
    try:
        value = int(horizon[:-1])
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid horizon format. Use format like '4w' or '30d'"
        )
    
    # Convert to days
    horizon_days = value * 7 if unit == 'w' else value
    
    if horizon_days > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Forecast horizon cannot exceed 365 days"
        )
    
    # Get historical sales data (last 90 days)
    lookback_date = datetime.utcnow() - timedelta(days=90)
    
    sales_data = db.query(
        func.date(Sale.timestamp).label('sale_date'),
        func.sum(Sale.quantity).label('total_quantity')
    ).filter(
        Sale.sku == sku,
        Sale.timestamp >= lookback_date
    ).group_by(
        func.date(Sale.timestamp)
    ).order_by(
        func.date(Sale.timestamp)
    ).all()
    
    if not sales_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No historical sales data found for SKU '{sku}' in the last 90 days"
        )
    
    # Convert to list of tuples
    historical_data = [(row.sale_date, float(row.total_quantity)) for row in sales_data]
    
    # Calculate forecast
    forecast_data = calculate_forecast(historical_data, horizon_days)
    
    # Calculate statistics
    historical_quantities = [qty for _, qty in historical_data]
    avg_daily_sales = np.mean(historical_quantities)
    
    return ForecastResponse(
        sku=sku,
        product_name=product.name,
        forecast_horizon_days=horizon_days,
        forecast=forecast_data,
        historical_avg_daily_sales=round(avg_daily_sales, 2),
        confidence_level=0.95
    )


@router.get("/forecast/summary")
async def get_forecast_summary(
    category: Optional[str] = Query(None, description="Filter by product category"),
    horizon: str = Query("4w", regex="^[1-9][0-9]*[wd]$", description="Forecast horizon"),
    db: Session = Depends(get_db)
) -> dict:
    """
    Get forecast summary for multiple products.
    
    Returns aggregated forecast information for products, optionally
    filtered by category. Useful for high-level planning.
    
    Args:
        category: Optional category filter
        horizon: Forecast horizon (format: <number><w|d>)
        db: Database session dependency
        
    Returns:
        dict: Aggregated forecast summary
    """
    # Parse horizon
    unit = horizon[-1]
    value = int(horizon[:-1])
    horizon_days = value * 7 if unit == 'w' else value
    
    # Get products
    query = db.query(Product).filter(Product.active == True)
    if category:
        query = query.filter(Product.category == category)
    
    products = query.all()
    
    total_forecast = 0
    products_forecasted = 0
    
    for product in products[:20]:  # Limit to top 20 products for performance
        lookback_date = datetime.utcnow() - timedelta(days=90)
        
        sales_data = db.query(
            func.date(Sale.timestamp).label('sale_date'),
            func.sum(Sale.quantity).label('total_quantity')
        ).filter(
            Sale.sku == product.sku,
            Sale.timestamp >= lookback_date
        ).group_by(
            func.date(Sale.timestamp)
        ).all()
        
        if sales_data:
            historical_data = [(row.sale_date, float(row.total_quantity)) for row in sales_data]
            forecast_data = calculate_forecast(historical_data, horizon_days)
            
            total_forecast += sum(point.value for point in forecast_data)
            products_forecasted += 1
    
    return {
        "category": category or "all",
        "horizon_days": horizon_days,
        "products_analyzed": products_forecasted,
        "total_forecasted_demand": round(total_forecast, 2),
        "avg_daily_demand": round(total_forecast / horizon_days, 2) if horizon_days > 0 else 0
    }