"""
Prophet model training, prediction, and evaluation utilities.
Handles model persistence and performance metrics.
"""
import pandas as pd
import numpy as np
from prophet import Prophet
import pickle
from typing import Dict, Optional
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def train_prophet(
    sku: str,
    df: pd.DataFrame,
    holidays_df: pd.DataFrame,
    regressors: Optional[list] = None
) -> Prophet:
    """
    Train Prophet model for a specific SKU.
    
    Args:
        sku: Product SKU identifier
        df: Training DataFrame with [ds, y] and optional regressor columns
        holidays_df: DataFrame with [ds, holiday] for custom holidays
        regressors: List of additional regressor column names
    
    Returns:
        Fitted Prophet model
    """
    logger.info(f"Training model for SKU {sku}")
    
    # Initialize Prophet with custom settings
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode='multiplicative',
        holidays=holidays_df if not holidays_df.empty else None,
        changepoint_prior_scale=0.05,
        seasonality_prior_scale=10.0,
        interval_width=0.95
    )
    
    # Add custom regressors if provided
    if regressors:
        for regressor in regressors:
            if regressor in df.columns:
                model.add_regressor(regressor, prior_scale=0.5)
                logger.info(f"Added regressor: {regressor}")
    
    # Add custom seasonality for ethnic wear market
    model.add_seasonality(
        name='monthly',
        period=30.5,
        fourier_order=5
    )
    
    # Fit model
    try:
        model.fit(df)
        logger.info(f"Successfully trained model for SKU {sku}")
        return model
    except Exception as e:
        logger.error(f"Error training model for SKU {sku}: {e}")
        raise


def predict_prophet(
    model: Prophet,
    horizon: int = 28,
    regressors_future: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Generate forecasts using trained Prophet model.
    
    Args:
        model: Trained Prophet model
        horizon: Number of days to forecast ahead (default: 28)
        regressors_future: DataFrame with future values for regressors
    
    Returns:
        DataFrame with [ds, yhat, yhat_lower, yhat_upper] columns
    """
    logger.info(f"Generating forecast for {horizon} days ahead")
    
    # Create future dataframe
    future = model.make_future_dataframe(periods=horizon, freq='D')
    
    # Add future regressor values if provided
    if regressors_future is not None:
        for col in regressors_future.columns:
            if col != 'ds' and col in future.columns:
                # Merge future regressor values
                future = future.merge(
                    regressors_future[['ds', col]],
                    on='ds',
                    how='left',
                    suffixes=('', '_future')
                )
                if f'{col}_future' in future.columns:
                    future[col] = future[f'{col}_future'].fillna(future[col])
                    future = future.drop(columns=f'{col}_future')
            elif col != 'ds':
                future[col] = 0  # Default value for missing regressors
    
    # Generate predictions
    forecast = model.predict(future)
    
    # Extract relevant columns and filter to future dates only
    result = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(horizon)
    
    # Ensure non-negative predictions
    result['yhat'] = result['yhat'].clip(lower=0)
    result['yhat_lower'] = result['yhat_lower'].clip(lower=0)
    result['yhat_upper'] = result['yhat_upper'].clip(lower=0)
    
    logger.info(f"Forecast complete: {len(result)} predictions generated")
    return result.reset_index(drop=True)


def save_model(model: Prophet, filepath: str) -> None:
    """
    Save trained Prophet model to disk using pickle.
    
    Args:
        model: Trained Prophet model
        filepath: Path to save the model (e.g., 'ml/models/prophet_sku123.pkl')
    """
    try:
        # Create directory if it doesn't exist
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump(model, f)
        
        logger.info(f"Model saved to {filepath}")
    except Exception as e:
        logger.error(f"Error saving model to {filepath}: {e}")
        raise


def load_model(filepath: str) -> Prophet:
    """
    Load trained Prophet model from disk.
    
    Args:
        filepath: Path to the saved model
    
    Returns:
        Loaded Prophet model
    """
    try:
        with open(filepath, 'rb') as f:
            model = pickle.load(f)
        
        logger.info(f"Model loaded from {filepath}")
        return model
    except Exception as e:
        logger.error(f"Error loading model from {filepath}: {e}")
        raise


def evaluate_model(actual: pd.Series, predicted: pd.Series) -> Dict[str, float]:
    """
    Calculate evaluation metrics for forecast accuracy.
    
    Args:
        actual: Actual values (y_true)
        predicted: Predicted values (y_pred)
    
    Returns:
        Dictionary with MAE, RMSE, and MAPE metrics
    """
    # Align series and remove NaN values
    mask = ~(actual.isna() | predicted.isna())
    actual = actual[mask]
    predicted = predicted[mask]
    
    if len(actual) == 0:
        logger.warning("No valid data points for evaluation")
        return {"MAE": np.nan, "RMSE": np.nan, "MAPE": np.nan}
    
    # Calculate metrics
    mae = np.mean(np.abs(actual - predicted))
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))
    
    # MAPE: avoid division by zero
    mask_nonzero = actual != 0
    if mask_nonzero.sum() > 0:
        mape = np.mean(np.abs((actual[mask_nonzero] - predicted[mask_nonzero]) / actual[mask_nonzero])) * 100
    else:
        mape = np.nan
    
    metrics = {
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2),
        "MAPE": round(mape, 2)
    }
    
    logger.info(f"Evaluation metrics: MAE={metrics['MAE']}, RMSE={metrics['RMSE']}, MAPE={metrics['MAPE']}%")
    return metrics


def cross_validate_model(
    model: Prophet,
    df: pd.DataFrame,
    horizon: int = 28,
    initial: int = 120,
    period: int = 14
) -> pd.DataFrame:
    """
    Perform time series cross-validation on Prophet model.
    
    Args:
        model: Trained Prophet model
        df: Training DataFrame
        horizon: Forecast horizon in days
        initial: Initial training period in days
        period: Spacing between cutoff dates in days
    
    Returns:
        DataFrame with cross-validation results
    """
    from prophet.diagnostics import cross_validation, performance_metrics
    
    logger.info("Starting cross-validation")
    
    try:
        cv_results = cross_validation(
            model,
            initial=f'{initial} days',
            period=f'{period} days',
            horizon=f'{horizon} days'
        )
        
        metrics = performance_metrics(cv_results)
        logger.info(f"Cross-validation complete: Mean MAPE={metrics['mape'].mean():.2f}%")
        
        return cv_results
    except Exception as e:
        logger.error(f"Error during cross-validation: {e}")
        return pd.DataFrame()