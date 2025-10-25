"""
Data loading utilities for fashion retail demand forecasting.
Handles fetching sales data, calendar events, and aggregations.
"""
import pandas as pd
from datetime import datetime
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_sales_timeseries(
    db, 
    sku: str, 
    start_date: str, 
    end_date: str
) -> pd.DataFrame:
    """
    Fetch daily sales timeseries for a specific SKU.
    
    Args:
        db: Database connection object
        sku: Product SKU identifier
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
    
    Returns:
        DataFrame with columns [ds, y] where ds=date, y=quantity
    """
    query = """
        SELECT 
            DATE(order_date) as ds,
            SUM(quantity) as y
        FROM sales
        WHERE sku = %s
            AND order_date BETWEEN %s AND %s
        GROUP BY DATE(order_date)
        ORDER BY ds
    """
    
    try:
        df = pd.read_sql_query(query, db, params=(sku, start_date, end_date))
        df['ds'] = pd.to_datetime(df['ds'])
        
        # Fill missing dates with 0 sales
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        df = df.set_index('ds').reindex(date_range, fill_value=0).reset_index()
        df.columns = ['ds', 'y']
        
        logger.info(f"Fetched {len(df)} days of sales data for SKU {sku}")
        return df
    except Exception as e:
        logger.error(f"Error fetching sales for SKU {sku}: {e}")
        return pd.DataFrame(columns=['ds', 'y'])


def fetch_calendar_events(db) -> pd.DataFrame:
    """
    Fetch calendar events (holidays, festivals) for Prophet.
    
    Args:
        db: Database connection object
    
    Returns:
        DataFrame with columns [ds, holiday] for Prophet's holidays parameter
    """
    query = """
        SELECT 
            DATE(event_date) as ds,
            event_name as holiday
        FROM calendar_events
        WHERE event_type IN ('holiday', 'festival')
        ORDER BY ds
    """
    
    try:
        df = pd.read_sql_query(query, db)
        df['ds'] = pd.to_datetime(df['ds'])
        
        # Add important Indian festivals if not in DB
        default_holidays = pd.DataFrame({
            'ds': pd.to_datetime([
                '2024-01-26', '2024-03-25', '2024-08-15', 
                '2024-10-02', '2024-10-24', '2024-11-01',
                '2025-01-26', '2025-03-14', '2025-08-15',
                '2025-10-02', '2025-10-12', '2025-11-01'
            ]),
            'holiday': [
                'Republic Day', 'Holi', 'Independence Day',
                'Gandhi Jayanti', 'Diwali', 'Diwali Week',
                'Republic Day', 'Holi', 'Independence Day',
                'Gandhi Jayanti', 'Diwali', 'Diwali Week'
            ]
        })
        
        df = pd.concat([df, default_holidays]).drop_duplicates(subset='ds')
        logger.info(f"Fetched {len(df)} calendar events")
        return df
    except Exception as e:
        logger.error(f"Error fetching calendar events: {e}")
        return pd.DataFrame(columns=['ds', 'holiday'])


def aggregate_to_weekly(df: pd.DataFrame) -> pd.DataFrame:
    """
    Resample daily data to weekly sums.
    
    Args:
        df: DataFrame with columns [ds, y]
    
    Returns:
        DataFrame with weekly aggregated data
    """
    if df.empty or 'ds' not in df.columns:
        logger.warning("Empty or invalid DataFrame provided")
        return pd.DataFrame(columns=['ds', 'y'])
    
    df = df.copy()
    df['ds'] = pd.to_datetime(df['ds'])
    df = df.set_index('ds')
    
    # Resample to weekly (Sunday to Saturday)
    weekly = df.resample('W-SAT').sum().reset_index()
    logger.info(f"Aggregated {len(df)} days to {len(weekly)} weeks")
    
    return weekly


def fetch_category_sales(
    db, 
    category: str, 
    start_date: str, 
    end_date: str
) -> pd.DataFrame:
    """
    Aggregate sales across all SKUs in a category.
    
    Args:
        db: Database connection object
        category: Product category (e.g., 'sarees', 'suits')
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
    
    Returns:
        DataFrame with columns [ds, y] aggregating all category SKUs
    """
    query = """
        SELECT 
            DATE(s.order_date) as ds,
            SUM(s.quantity) as y
        FROM sales s
        JOIN products p ON s.sku = p.sku
        WHERE p.category = %s
            AND s.order_date BETWEEN %s AND %s
        GROUP BY DATE(s.order_date)
        ORDER BY ds
    """
    
    try:
        df = pd.read_sql_query(query, db, params=(category, start_date, end_date))
        df['ds'] = pd.to_datetime(df['ds'])
        
        # Fill missing dates with 0 sales
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        df = df.set_index('ds').reindex(date_range, fill_value=0).reset_index()
        df.columns = ['ds', 'y']
        
        logger.info(f"Fetched {len(df)} days of category sales for {category}")
        return df
    except Exception as e:
        logger.error(f"Error fetching category sales for {category}: {e}")
        return pd.DataFrame(columns=['ds', 'y'])