"""
Inference API for demand forecasting.
Handles loading models, generating predictions, and batch forecasting.
"""
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta

from ml.prophet_model import load_model, predict_prophet
from ml.data_loader import (
    fetch_sales_timeseries, 
    fetch_category_sales,
    fetch_calendar_events
)
from ml.features import add_season_features, add_promotion_flags

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODELS_DIR = Path("ml/models")
MIN_DATA_DAYS = 60


def get_forecast(
    db,
    sku: str,
    horizon: int = 28,
    include_regressors: bool = True
) -> Dict:
    """
    Get demand forecast for a specific SKU.
    
    Args:
        db: Database connection object
        sku: Product SKU identifier
        horizon: Number of days to forecast ahead
        include_regressors: Whether to include regressor values in future predictions
    
    Returns:
        Dictionary with forecast data:
        {
            "sku": str,
            "forecast": [
                {"date": str, "value": float, "lower": float, "upper": float},
                ...
            ],
            "model_path": str,
            "generated_at": str
        }
    """
    logger.info(f"Generating forecast for SKU {sku}")
    
    # Check if model exists
    model_path = MODELS_DIR / f"prophet_{sku}.pkl"
    
    if not model_path.exists():
        logger.warning(f"Model not found for SKU {sku} at {model_path}")
        return {
            "sku": sku,
            "error": "Model not found. Please train the model first.",
            "forecast": []
        }
    
    try:
        # Load trained model
        model = load_model(str(model_path))
        
        # Prepare future regressors if needed
        regressors_future = None
        if include_regressors:
            future_dates = pd.date_range(
                start=datetime.now().date(),
                periods=horizon,
                freq='D'
            )
            regressors_future = pd.DataFrame({'ds': future_dates})
            
            # Add seasonal features
            regressors_future = add_season_features(regressors_future)
            
            # Add promotion flags (assuming no future promos, set to 0)
            regressors_future['is_promo'] = 0
            
            # Lag features will be 0 for future (unknown)
            regressors_future['y_lag_7'] = 0
            regressors_future['y_rolling_mean_7'] = 0
        
        # Generate predictions
        forecast_df = predict_prophet(model, horizon=horizon, regressors_future=regressors_future)
        
        # Format output
        forecast_list = []
        for _, row in forecast_df.iterrows():
            forecast_list.append({
                "date": row['ds'].strftime('%Y-%m-%d'),
                "value": round(row['yhat'], 2),
                "lower": round(row['yhat_lower'], 2),
                "upper": round(row['yhat_upper'], 2)
            })
        
        result = {
            "sku": sku,
            "forecast": forecast_list,
            "model_path": str(model_path),
            "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "horizon_days": horizon
        }
        
        logger.info(f"Forecast generated successfully for SKU {sku}")
        return result
        
    except Exception as e:
        logger.error(f"Error generating forecast for SKU {sku}: {e}")
        return {
            "sku": sku,
            "error": str(e),
            "forecast": []
        }


def batch_forecast_all_skus(
    db,
    horizon: int = 28,
    save_to_db: bool = True,
    active_only: bool = True
) -> None:
    """
    Generate forecasts for all SKUs and optionally save to database.
    
    Args:
        db: Database connection object
        horizon: Number of days to forecast ahead
        save_to_db: Whether to save forecasts to database
        active_only: Only forecast for active products
    """
    logger.info("Starting batch forecast for all SKUs")
    
    # Fetch all active SKUs
    query = """
        SELECT DISTINCT sku, category
        FROM products
        WHERE is_active = TRUE
    """ if active_only else """
        SELECT DISTINCT sku, category
        FROM products
    """
    
    try:
        skus_df = pd.read_sql_query(query, db)
        total_skus = len(skus_df)
        logger.info(f"Found {total_skus} SKUs to forecast")
        
        successful = 0
        failed = 0
        sparse_data = 0
        
        for idx, row in skus_df.iterrows():
            sku = row['sku']
            category = row['category']
            
            logger.info(f"Processing {idx+1}/{total_skus}: SKU {sku}")
            
            # Check for sparse data
            data_status = handle_sparse_data(db, sku)
            
            if data_status == "insufficient":
                logger.warning(f"Insufficient data for SKU {sku}, using category fallback")
                sparse_data += 1
                continue
            
            # Generate forecast
            forecast_result = get_forecast(db, sku, horizon=horizon)
            
            if "error" in forecast_result:
                logger.warning(f"Failed to forecast SKU {sku}: {forecast_result['error']}")
                failed += 1
                continue
            
            # Save to database if requested
            if save_to_db and forecast_result['forecast']:
                save_forecast_to_db(db, forecast_result)
            
            successful += 1
        
        logger.info(
            f"Batch forecast complete: {successful} successful, "
            f"{failed} failed, {sparse_data} sparse data"
        )
        
    except Exception as e:
        logger.error(f"Error in batch forecasting: {e}")
        raise


def handle_sparse_data(db, sku: str) -> str:
    """
    Check if SKU has sufficient historical data.
    
    Args:
        db: Database connection object
        sku: Product SKU identifier
    
    Returns:
        Status string: "sufficient", "insufficient", or "use_category"
    """
    # Check data availability
    query = """
        SELECT 
            MIN(order_date) as first_sale,
            MAX(order_date) as last_sale,
            COUNT(DISTINCT DATE(order_date)) as days_with_sales
        FROM sales
        WHERE sku = %s
    """
    
    try:
        result = pd.read_sql_query(query, db, params=(sku,))
        
        if result.empty or result['days_with_sales'].iloc[0] is None:
            logger.warning(f"No sales data found for SKU {sku}")
            return "insufficient"
        
        days_with_sales = result['days_with_sales'].iloc[0]
        
        if days_with_sales < MIN_DATA_DAYS:
            logger.warning(
                f"SKU {sku} has only {days_with_sales} days of sales data "
                f"(minimum: {MIN_DATA_DAYS})"
            )
            return "insufficient"
        
        return "sufficient"
        
    except Exception as e:
        logger.error(f"Error checking data for SKU {sku}: {e}")
        return "insufficient"


def get_category_forecast(
    db,
    category: str,
    horizon: int = 28
) -> Dict:
    """
    Generate forecast at category level (for SKUs with sparse data).
    
    Args:
        db: Database connection object
        category: Product category (e.g., 'sarees', 'suits')
        horizon: Number of days to forecast ahead
    
    Returns:
        Dictionary with category-level forecast
    """
    logger.info(f"Generating category-level forecast for {category}")
    
    # Check if category model exists
    model_path = MODELS_DIR / f"prophet_category_{category}.pkl"
    
    if not model_path.exists():
        logger.warning(f"Category model not found for {category}")
        return {
            "category": category,
            "error": "Category model not found",
            "forecast": []
        }
    
    try:
        model = load_model(str(model_path))
        forecast_df = predict_prophet(model, horizon=horizon)
        
        forecast_list = []
        for _, row in forecast_df.iterrows():
            forecast_list.append({
                "date": row['ds'].strftime('%Y-%m-%d'),
                "value": round(row['yhat'], 2),
                "lower": round(row['yhat_lower'], 2),
                "upper": round(row['yhat_upper'], 2)
            })
        
        return {
            "category": category,
            "forecast": forecast_list,
            "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        logger.error(f"Error generating category forecast for {category}: {e}")
        return {
            "category": category,
            "error": str(e),
            "forecast": []
        }


def save_forecast_to_db(db, forecast_result: Dict) -> None:
    """
    Save forecast results to database cache table.
    
    Args:
        db: Database connection object
        forecast_result: Dictionary with forecast data
    """
    if not forecast_result.get('forecast'):
        return
    
    try:
        cursor = db.cursor()
        
        for item in forecast_result['forecast']:
            query = """
                INSERT INTO forecast_cache 
                (sku, forecast_date, forecast_value, lower_bound, upper_bound, generated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (sku, forecast_date) 
                DO UPDATE SET
                    forecast_value = EXCLUDED.forecast_value,
                    lower_bound = EXCLUDED.lower_bound,
                    upper_bound = EXCLUDED.upper_bound,
                    generated_at = EXCLUDED.generated_at
            """
            
            cursor.execute(query, (
                forecast_result['sku'],
                item['date'],
                item['value'],
                item['lower'],
                item['upper'],
                forecast_result['generated_at']
            ))
        
        db.commit()
        logger.info(f"Saved {len(forecast_result['forecast'])} forecasts to database")
        
    except Exception as e:
        logger.error(f"Error saving forecast to database: {e}")
        db.rollback()


def get_bulk_forecasts(
    db,
    skus: List[str],
    horizon: int = 28
) -> List[Dict]:
    """
    Get forecasts for multiple SKUs in bulk.
    
    Args:
        db: Database connection object
        skus: List of SKU identifiers
        horizon: Number of days to forecast ahead
    
    Returns:
        List of forecast dictionaries
    """
    logger.info(f"Generating bulk forecasts for {len(skus)} SKUs")
    
    results = []
    for sku in skus:
        forecast = get_forecast(db, sku, horizon=horizon)
        results.append(forecast)
    
    return results