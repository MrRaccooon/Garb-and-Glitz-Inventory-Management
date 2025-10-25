"""
Import Service Module
Handles CSV validation and bulk data import operations.
"""

from typing import Dict, List, Optional, BinaryIO
from datetime import datetime
from sqlalchemy.orm import Session
import logging
import pandas as pd
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_csv(file: BinaryIO, expected_columns: List[str]) -> bool:
    """
    Validate CSV file structure and basic data types.
    
    Args:
        file: File object (binary mode)
        expected_columns: List of required column names
        
    Returns:
        True if valid, raises ValueError if invalid
        
    Example:
        >>> with open('sales.csv', 'rb') as f:
        ...     is_valid = validate_csv(f, ['sku', 'quantity', 'timestamp'])
    """
    try:
        # Read CSV into pandas DataFrame
        df = pd.read_csv(file, encoding='utf-8')
        
        # Reset file pointer for subsequent reads
        file.seek(0)
        
        # Check if DataFrame is empty
        if df.empty:
            raise ValueError("CSV file is empty")
        
        # Strip whitespace from column names
        df.columns = df.columns.str.strip()
        
        # Check for required columns
        missing_columns = set(expected_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(
                f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # Check for duplicate columns
        duplicate_cols = df.columns[df.columns.duplicated()].tolist()
        if duplicate_cols:
            raise ValueError(
                f"Duplicate columns found: {', '.join(duplicate_cols)}"
            )
        
        logger.info(
            f"CSV validation passed: {len(df)} rows, "
            f"columns: {', '.join(df.columns)}"
        )
        
        return True
        
    except pd.errors.EmptyDataError:
        raise ValueError("CSV file is empty or invalid")
    except pd.errors.ParserError as e:
        raise ValueError(f"CSV parsing error: {str(e)}")
    except Exception as e:
        logger.error(f"CSV validation error: {str(e)}")
        raise


def import_sales_csv(db: Session, file: BinaryIO) -> Dict:
    """
    Import sales data from CSV file with validation and bulk insert.
    Expected columns: sku, quantity, timestamp (optional)
    
    Args:
        db: SQLAlchemy database session
        file: CSV file object (binary mode)
        
    Returns:
        Dictionary with import statistics and errors
        
    Example:
        >>> with open('sales_data.csv', 'rb') as f:
        ...     result = import_sales_csv(db, f)
        >>> print(f"Imported: {result['imported']}, Errors: {len(result['errors'])}")
    """
    imported_count = 0
    errors = []
    
    try:
        from models import Sale, Product
        from services.inventory_service import get_current_stock
        
        # Validate CSV structure
        required_columns = ['sku', 'quantity']
        validate_csv(file, required_columns)
        
        # Read CSV with pandas
        df = pd.read_csv(file, encoding='utf-8')
        df.columns = df.columns.str.strip()
        
        # Add timestamp if not present
        if 'timestamp' not in df.columns:
            df['timestamp'] = datetime.now()
        else:
            # Parse timestamp column
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        # Clean data
        df['sku'] = df['sku'].astype(str).str.strip()
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
        
        # Get all valid SKUs from database for validation
        valid_skus = set(
            sku[0] for sku in db.query(Product.sku).all()
        )
        
        logger.info(f"Processing {len(df)} sales records...")
        
        # Process each row
        for idx, row in df.iterrows():
            try:
                # Validate data
                if pd.isna(row['sku']) or row['sku'] == '':
                    errors.append({
                        "row": idx + 2,  # +2 for header and 0-index
                        "error": "Missing SKU"
                    })
                    continue
                
                if pd.isna(row['quantity']) or row['quantity'] <= 0:
                    errors.append({
                        "row": idx + 2,
                        "error": f"Invalid quantity: {row['quantity']}"
                    })
                    continue
                
                if row['sku'] not in valid_skus:
                    errors.append({
                        "row": idx + 2,
                        "error": f"SKU not found: {row['sku']}"
                    })
                    continue
                
                if pd.isna(row['timestamp']):
                    errors.append({
                        "row": idx + 2,
                        "error": "Invalid timestamp format"
                    })
                    continue
                
                # Check stock availability
                current_stock = get_current_stock(db, row['sku'])
                if current_stock < row['quantity']:
                    errors.append({
                        "row": idx + 2,
                        "error": f"Insufficient stock for {row['sku']} "
                                f"(available: {current_stock}, requested: {row['quantity']})"
                    })
                    continue
                
                # Create sale record
                sale = Sale(
                    sku=row['sku'],
                    quantity=int(row['quantity']),
                    timestamp=row['timestamp']
                )
                db.add(sale)
                db.flush()
                
                # Create inventory ledger entry
                from models import InventoryLedger
                new_balance = current_stock - int(row['quantity'])
                
                ledger_entry = InventoryLedger(
                    sku=row['sku'],
                    change_qty=-int(row['quantity']),
                    balance_qty=new_balance,
                    reason=f"Sale #{sale.sale_id} (CSV Import)",
                    timestamp=row['timestamp']
                )
                db.add(ledger_entry)
                
                imported_count += 1
                
                # Commit in batches of 100
                if imported_count % 100 == 0:
                    db.commit()
                    logger.info(f"Committed {imported_count} records...")
                
            except Exception as e:
                errors.append({
                    "row": idx + 2,
                    "error": str(e)
                })
                db.rollback()
        
        # Final commit
        db.commit()
        
        logger.info(
            f"Sales import completed: {imported_count} imported, "
            f"{len(errors)} errors"
        )
        
        return {
            "imported": imported_count,
            "errors": errors,
            "total_rows": len(df)
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error importing sales CSV: {str(e)}")
        raise


def import_products_csv(db: Session, file: BinaryIO) -> Dict:
    """
    Import product data from CSV file with validation and bulk insert.
    Expected columns: sku, name, cost_price, sell_price, reorder_point (optional), lead_time_days (optional)
    
    Args:
        db: SQLAlchemy database session
        file: CSV file object (binary mode)
        
    Returns:
        Dictionary with import statistics and errors
        
    Example:
        >>> with open('products.csv', 'rb') as f:
        ...     result = import_products_csv(db, f)
        >>> print(f"Imported: {result['imported']}, Updated: {result['updated']}")
    """
    imported_count = 0
    updated_count = 0
    errors = []
    
    try:
        from models import Product
        
        # Validate CSV structure
        required_columns = ['sku', 'name', 'cost_price', 'sell_price']
        validate_csv(file, required_columns)
        
        # Read CSV with pandas
        df = pd.read_csv(file, encoding='utf-8')
        df.columns = df.columns.str.strip()
        
        # Clean and validate data
        df['sku'] = df['sku'].astype(str).str.strip()
        df['name'] = df['name'].astype(str).str.strip()
        df['cost_price'] = pd.to_numeric(df['cost_price'], errors='coerce')
        df['sell_price'] = pd.to_numeric(df['sell_price'], errors='coerce')
        
        # Handle optional columns
        if 'reorder_point' in df.columns:
            df['reorder_point'] = pd.to_numeric(df['reorder_point'], errors='coerce')
        else:
            df['reorder_point'] = None
        
        if 'lead_time_days' in df.columns:
            df['lead_time_days'] = pd.to_numeric(df['lead_time_days'], errors='coerce')
        else:
            df['lead_time_days'] = 7  # Default
        
        logger.info(f"Processing {len(df)} product records...")
        
        # Get existing SKUs for update detection
        existing_skus = set(
            sku[0] for sku in db.query(Product.sku).all()
        )
        
        # Process each row
        for idx, row in df.iterrows():
            try:
                # Validate data
                if pd.isna(row['sku']) or row['sku'] == '':
                    errors.append({
                        "row": idx + 2,
                        "error": "Missing SKU"
                    })
                    continue
                
                if pd.isna(row['name']) or row['name'] == '':
                    errors.append({
                        "row": idx + 2,
                        "error": "Missing product name"
                    })
                    continue
                
                if pd.isna(row['cost_price']) or row['cost_price'] < 0:
                    errors.append({
                        "row": idx + 2,
                        "error": f"Invalid cost_price: {row['cost_price']}"
                    })
                    continue
                
                if pd.isna(row['sell_price']) or row['sell_price'] < 0:
                    errors.append({
                        "row": idx + 2,
                        "error": f"Invalid sell_price: {row['sell_price']}"
                    })
                    continue
                
                # Check if product exists (update) or new (insert)
                if row['sku'] in existing_skus:
                    # Update existing product
                    product = db.query(Product).filter(
                        Product.sku == row['sku']
                    ).first()
                    
                    product.name = row['name']
                    product.cost_price = float(row['cost_price'])
                    product.sell_price = float(row['sell_price'])
                    
                    if not pd.isna(row['reorder_point']):
                        product.reorder_point = int(row['reorder_point'])
                    
                    if not pd.isna(row['lead_time_days']):
                        product.lead_time_days = int(row['lead_time_days'])
                    
                    updated_count += 1
                    
                else:
                    # Create new product
                    product = Product(
                        sku=row['sku'],
                        name=row['name'],
                        cost_price=float(row['cost_price']),
                        sell_price=float(row['sell_price']),
                        reorder_point=int(row['reorder_point']) if not pd.isna(row['reorder_point']) else None,
                        lead_time_days=int(row['lead_time_days']) if not pd.isna(row['lead_time_days']) else 7
                    )
                    db.add(product)
                    existing_skus.add(row['sku'])
                    imported_count += 1
                
                # Commit in batches of 100
                if (imported_count + updated_count) % 100 == 0:
                    db.commit()
                    logger.info(f"Committed {imported_count + updated_count} records...")
                
            except Exception as e:
                errors.append({
                    "row": idx + 2,
                    "error": str(e)
                })
                db.rollback()
        
        # Final commit
        db.commit()
        
        logger.info(
            f"Products import completed: {imported_count} new, "
            f"{updated_count} updated, {len(errors)} errors"
        )
        
        return {
            "imported": imported_count,
            "updated": updated_count,
            "errors": errors,
            "total_rows": len(df)
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error importing products CSV: {str(e)}")
        raise