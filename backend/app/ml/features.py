"""
Feature engineering utilities for demand forecasting.
Adds holiday flags, promotion flags, seasonal features, and lag features.
"""
import pandas as pd
import numpy as np
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_holiday_flags(
    df: pd.DataFrame, 
    holidays_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge calendar events and create binary holiday flag.
    
    Args:
        df: Sales DataFrame with 'ds' column
        holidays_df: DataFrame with [ds, holiday] columns
    
    Returns:
        DataFrame with added 'is_holiday' column (0/1)
    """
    df = df.copy()
    df['ds'] = pd.to_datetime(df['ds'])
    holidays_df = holidays_df.copy()
    holidays_df['ds'] = pd.to_datetime(holidays_df['ds'])
    
    # Mark holidays
    holidays_df['is_holiday'] = 1
    df = df.merge(
        holidays_df[['ds', 'is_holiday']].drop_duplicates(subset='ds'),
        on='ds',
        how='left'
    )
    df['is_holiday'] = df['is_holiday'].fillna(0).astype(int)
    
    logger.info(f"Added holiday flags: {df['is_holiday'].sum()} holiday days")
    return df


def add_promotion_flags(
    df: pd.DataFrame, 
    promotions_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Add promotion flags to indicate promotional periods.
    
    Args:
        df: Sales DataFrame with 'ds' column
        promotions_df: DataFrame with [start_date, end_date, sku] or [start_date, end_date] for all SKUs
    
    Returns:
        DataFrame with added 'is_promo' column (0/1)
    """
    df = df.copy()
    df['ds'] = pd.to_datetime(df['ds'])
    df['is_promo'] = 0
    
    if promotions_df.empty:
        logger.info("No promotions found")
        return df
    
    promotions_df = promotions_df.copy()
    promotions_df['start_date'] = pd.to_datetime(promotions_df['start_date'])
    promotions_df['end_date'] = pd.to_datetime(promotions_df['end_date'])
    
    # Mark promo periods
    for _, promo in promotions_df.iterrows():
        mask = (df['ds'] >= promo['start_date']) & (df['ds'] <= promo['end_date'])
        df.loc[mask, 'is_promo'] = 1
    
    logger.info(f"Added promotion flags: {df['is_promo'].sum()} promo days")
    return df


def add_season_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add seasonal features specific to Indian ethnic wear market.
    
    Args:
        df: Sales DataFrame with 'ds' column
    
    Returns:
        DataFrame with added 'is_wedding_season' and 'is_festival_season' columns
    """
    df = df.copy()
    df['ds'] = pd.to_datetime(df['ds'])
    df['month'] = df['ds'].dt.month
    
    # Wedding season: October to February (peak demand for sarees/suits)
    df['is_wedding_season'] = df['month'].isin([10, 11, 12, 1, 2]).astype(int)
    
    # Festival season: August to November (Raksha Bandhan, Navratri, Diwali, etc.)
    df['is_festival_season'] = df['month'].isin([8, 9, 10, 11]).astype(int)
    
    # Add festival intensity (combined metric)
    df['season_intensity'] = (
        df['is_wedding_season'] * 0.6 + 
        df['is_festival_season'] * 0.4
    )
    
    # Cleanup temporary column
    df = df.drop(columns=['month'])
    
    logger.info("Added seasonal features: wedding and festival seasons")
    return df


def create_lag_features(
    df: pd.DataFrame, 
    lags: List[int] = [7, 14, 30]
) -> pd.DataFrame:
    """
    Create lag features for time series data.
    
    Args:
        df: Sales DataFrame with 'ds' and 'y' columns
        lags: List of lag periods in days (default: [7, 14, 30])
    
    Returns:
        DataFrame with added lag columns: y_lag_7, y_lag_14, y_lag_30
    """
    df = df.copy()
    df = df.sort_values('ds').reset_index(drop=True)
    
    for lag in lags:
        col_name = f'y_lag_{lag}'
        df[col_name] = df['y'].shift(lag)
    
    # Add rolling statistics
    df['y_rolling_mean_7'] = df['y'].rolling(window=7, min_periods=1).mean()
    df['y_rolling_std_7'] = df['y'].rolling(window=7, min_periods=1).std()
    df['y_rolling_mean_30'] = df['y'].rolling(window=30, min_periods=1).mean()
    
    # Fill NaN with 0 (for initial periods)
    lag_cols = [f'y_lag_{lag}' for lag in lags]
    df[lag_cols] = df[lag_cols].fillna(0)
    
    rolling_cols = ['y_rolling_std_7']
    df[rolling_cols] = df[rolling_cols].fillna(0)
    
    logger.info(f"Created lag features: {lags}")
    return df


def prepare_prophet_regressors(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare additional regressors for Prophet model.
    Combines promotion, season, and lag features.
    
    Args:
        df: DataFrame with all features
    
    Returns:
        DataFrame ready for Prophet with selected regressors
    """
    df = df.copy()
    
    # Ensure required columns exist
    required_cols = ['ds', 'y']
    regressor_cols = [
        'is_promo', 'is_wedding_season', 'is_festival_season',
        'y_lag_7', 'y_rolling_mean_7'
    ]
    
    missing_cols = [col for col in regressor_cols if col not in df.columns]
    if missing_cols:
        logger.warning(f"Missing regressor columns: {missing_cols}")
    
    # Select available columns
    available_regressors = [col for col in regressor_cols if col in df.columns]
    output_cols = required_cols + available_regressors
    
    logger.info(f"Prepared {len(available_regressors)} regressors for Prophet")
    return df[output_cols]