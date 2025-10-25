"""
Training script for Prophet demand forecasting models.
Supports training single SKU or batch training all SKUs.

Usage:
    python training_script.py --sku SKU123          # Train single SKU
    python training_script.py --all                  # Train all active SKUs
    python training_script.py --category sarees      # Train category model
    python training_script.py --all --evaluate       # Train and evaluate
"""
import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import logging

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from ml.data_loader import (
    fetch_sales_timeseries,
    fetch_calendar_events,
    fetch_category_sales
)
from ml.features import (
    add_holiday_flags,
    add_promotion_flags,
    add_season_features,
    create_lag_features
)
from ml.prophet_model import (
    train_prophet,
    predict_prophet,
    save_model,
    evaluate_model
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ml/logs/training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

MODELS_DIR = Path("ml/models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

Path("ml/logs").mkdir(parents=True, exist_ok=True)

MIN_DATA_DAYS = 60
EVALUATION_PERIOD_DAYS = 28


def get_database_connection():
    """
    Establish database connection.
    Update with your actual database credentials.
    """
    import psycopg2
    # Example for PostgreSQL
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fashion_retail",
            user="your_username",
            password="your_password"
        )
        logger.info("Database connection established")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


def fetch_promotions_data(db, sku: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch promotion data for a SKU.
    """
    query = """
        SELECT 
            start_date,
            end_date
        FROM promotions
        WHERE (sku = %s OR sku IS NULL)
            AND start_date <= %s
            AND end_date >= %s
    """
    try:
        df = pd.read_sql_query(query, db, params=(sku, end_date, start_date))
        return df
    except Exception as e:
        logger.warning(f"Could not fetch promotions for {sku}: {e}")
        return pd.DataFrame(columns=['start_date', 'end_date'])


def train_single_sku(
    db,
    sku: str,
    evaluate: bool = True
) -> dict:
    """
    Train Prophet model for a single SKU.
    
    Args:
        db: Database connection
        sku: Product SKU identifier
        evaluate: Whether to evaluate on holdout data
    
    Returns:
        Dictionary with training results and metrics
    """
    logger.info(f"Starting training for SKU {sku}")
    
    # Define date range (last 6 months)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=180)
    
    # Fetch sales data
    sales_df = fetch_sales_timeseries(
        db, sku, 
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )
    
    if sales_df.empty or len(sales_df) < MIN_DATA_DAYS:
        logger.warning(f"Insufficient data for SKU {sku}: {len(sales_df)} days")
        return {
            "sku": sku,
            "status": "insufficient_data",
            "days_available": len(sales_df)
        }
    
    # Fetch calendar events
    holidays_df = fetch_calendar_events(db)
    
    # Fetch promotions
    promotions_df = fetch_promotions_data(
        db, sku,
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )
    
    # Feature engineering
    sales_df = add_holiday_flags(sales_df, holidays_df)
    sales_df = add_promotion_flags(sales_df, promotions_df)
    sales_df = add_season_features(sales_df)
    sales_df = create_lag_features(sales_df, lags=[7, 14, 30])
    
    # Split data for evaluation
    if evaluate:
        split_date = end_date - timedelta(days=EVALUATION_PERIOD_DAYS)
        train_df = sales_df[sales_df['ds'] < pd.Timestamp(split_date)]
        test_df = sales_df[sales_df['ds'] >= pd.Timestamp(split_date)]
    else:
        train_df = sales_df
        test_df = pd.DataFrame()
    
    # Define regressors
    regressors = [
        'is_promo',
        'is_wedding_season',
        'is_festival_season',
        'y_lag_7',
        'y_rolling_mean_7'
    ]
    
    # Train model
    try:
        model = train_prophet(sku, train_df, holidays_df, regressors=regressors)
        
        # Save model
        model_path = MODELS_DIR / f"prophet_{sku}.pkl"
        save_model(model, str(model_path))
        
        # Evaluate if requested
        metrics = {}
        if evaluate and not test_df.empty:
            # Prepare future regressors for test period
            test_regressors = test_df[['ds'] + regressors].copy()
            
            # Make predictions
            forecast = predict_prophet(model, horizon=len(test_df), regressors_future=test_regressors)
            
            # Calculate metrics
            metrics = evaluate_model(test_df['y'], forecast['yhat'])
            logger.info(f"SKU {sku} - MAE: {metrics['MAE']}, RMSE: {metrics['RMSE']}, MAPE: {metrics['MAPE']}%")
        
        return {
            "sku": sku,
            "status": "success",
            "model_path": str(model_path),
            "training_samples": len(train_df),
            "metrics": metrics
        }
        
    except Exception as e:
        logger.error(f"Error training SKU {sku}: {e}")
        return {
            "sku": sku,
            "status": "error",
            "error": str(e)
        }


def train_all_skus(db, evaluate: bool = True) -> None:
    """
    Train models for all active SKUs.
    """
    logger.info("Starting batch training for all SKUs")
    
    # Fetch all active SKUs
    query = """
        SELECT DISTINCT sku, category
        FROM products
        WHERE is_active = TRUE
        ORDER BY sku
    """
    
    try:
        skus_df = pd.read_sql_query(query, db)
        total_skus = len(skus_df)
        logger.info(f"Found {total_skus} active SKUs")
        
        results = {
            "successful": [],
            "insufficient_data": [],
            "failed": []
        }
        
        for idx, row in skus_df.iterrows():
            sku = row['sku']
            logger.info(f"\nProcessing {idx+1}/{total_skus}: SKU {sku}")
            
            result = train_single_sku(db, sku, evaluate=evaluate)
            
            if result['status'] == 'success':
                results['successful'].append(result)
            elif result['status'] == 'insufficient_data':
                results['insufficient_data'].append(result)
            else:
                results['failed'].append(result)
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("TRAINING SUMMARY")
        logger.info("="*60)
        logger.info(f"Total SKUs: {total_skus}")
        logger.info(f"Successful: {len(results['successful'])}")
        logger.info(f"Insufficient Data: {len(results['insufficient_data'])}")
        logger.info(f"Failed: {len(results['failed'])}")
        
        # Average metrics for successful models
        if results['successful'] and evaluate:
            avg_mae = sum(r['metrics'].get('MAE', 0) for r in results['successful']) / len(results['successful'])
            avg_rmse = sum(r['metrics'].get('RMSE', 0) for r in results['successful']) / len(results['successful'])
            avg_mape = sum(r['metrics'].get('MAPE', 0) for r in results['successful']) / len(results['successful'])
            
            logger.info(f"\nAverage Metrics:")
            logger.info(f"MAE: {avg_mae:.2f}")
            logger.info(f"RMSE: {avg_rmse:.2f}")
            logger.info(f"MAPE: {avg_mape:.2f}%")
        
        # Save summary
        summary_df = pd.DataFrame({
            'status': ['successful', 'insufficient_data', 'failed'],
            'count': [
                len(results['successful']),
                len(results['insufficient_data']),
                len(results['failed'])
            ]
        })
        summary_df.to_csv('ml/logs/training_summary.csv', index=False)
        logger.info("\nSummary saved to ml/logs/training_summary.csv")
        
    except Exception as e:
        logger.error(f"Error in batch training: {e}")
        raise


def train_category_model(db, category: str, evaluate: bool = True) -> dict:
    """
    Train Prophet model at category level.
    """
    logger.info(f"Training category model for {category}")
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=180)
    
    # Fetch aggregated category sales
    sales_df = fetch_category_sales(
        db, category,
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )
    
    if sales_df.empty:
        logger.warning(f"No data for category {category}")
        return {"category": category, "status": "no_data"}
    
    # Fetch calendar events
    holidays_df = fetch_calendar_events(db)
    
    # Feature engineering
    sales_df = add_holiday_flags(sales_df, holidays_df)
    sales_df = add_season_features(sales_df)
    
    # Split for evaluation
    if evaluate:
        split_date = end_date - timedelta(days=EVALUATION_PERIOD_DAYS)
        train_df = sales_df[sales_df['ds'] < pd.Timestamp(split_date)]
        test_df = sales_df[sales_df['ds'] >= pd.Timestamp(split_date)]
    else:
        train_df = sales_df
        test_df = pd.DataFrame()
    
    # Train
    try:
        model = train_prophet(
            f"category_{category}",
            train_df,
            holidays_df,
            regressors=['is_wedding_season', 'is_festival_season']
        )
        
        model_path = MODELS_DIR / f"prophet_category_{category}.pkl"
        save_model(model, str(model_path))
        
        metrics = {}
        if evaluate and not test_df.empty:
            forecast = predict_prophet(model, horizon=len(test_df))
            metrics = evaluate_model(test_df['y'], forecast['yhat'])
            logger.info(f"Category {category} - MAE: {metrics['MAE']}")
        
        return {
            "category": category,
            "status": "success",
            "model_path": str(model_path),
            "metrics": metrics
        }
        
    except Exception as e:
        logger.error(f"Error training category {category}: {e}")
        return {"category": category, "status": "error", "error": str(e)}


def main():
    """Main training function with CLI arguments."""
    parser = argparse.ArgumentParser(
        description='Train Prophet models for demand forecasting'
    )
    parser.add_argument(
        '--sku',
        type=str,
        help='Train model for a single SKU'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Train models for all active SKUs'
    )
    parser.add_argument(
        '--category',
        type=str,
        help='Train category-level model (e.g., sarees, suits)'
    )
    parser.add_argument(
        '--evaluate',
        action='store_true',
        default=True,
        help='Evaluate models on last 4 weeks (default: True)'
    )
    parser.add_argument(
        '--no-evaluate',
        action='store_true',
        help='Skip evaluation'
    )
    
    args = parser.parse_args()
    
    # Handle no-evaluate flag
    evaluate = args.evaluate and not args.no_evaluate
    
    # Connect to database
    try:
        db = get_database_connection()
    except Exception as e:
        logger.error(f"Cannot proceed without database connection: {e}")
        sys.exit(1)
    
    # Execute training based on arguments
    try:
        if args.sku:
            result = train_single_sku(db, args.sku, evaluate=evaluate)
            logger.info(f"\nTraining result: {result}")
            
        elif args.all:
            train_all_skus(db, evaluate=evaluate)
            
        elif args.category:
            result = train_category_model(db, args.category, evaluate=evaluate)
            logger.info(f"\nCategory training result: {result}")
            
        else:
            parser.print_help()
            logger.info("\nPlease specify --sku, --all, or --category")
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        sys.exit(1)
    
    finally:
        db.close()
        logger.info("Database connection closed")


if __name__ == "__main__":
    main()