"""
Inventory Service Module
Handles stock tracking, sales recording, and inventory valuation operations.
"""

from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_current_stock(db: Session, sku: str) -> int:
    """
    Get current stock level for a specific SKU by summing ledger entries.
    
    Args:
        db: SQLAlchemy database session
        sku: Product SKU identifier
        
    Returns:
        Current stock quantity (integer)
        
    Example:
        >>> stock = get_current_stock(db, "WIDGET-001")
        >>> print(f"Current stock: {stock}")
    """
    try:
        from models import InventoryLedger
        
        result = db.query(func.sum(InventoryLedger.change_qty)).filter(
            InventoryLedger.sku == sku
        ).scalar()
        
        return result if result is not None else 0
        
    except Exception as e:
        logger.error(f"Error fetching stock for SKU {sku}: {str(e)}")
        raise


def get_all_stock(db: Session) -> List[Dict]:
    """
    Get aggregated stock levels for all products with status indicators.
    
    Args:
        db: SQLAlchemy database session
        
    Returns:
        List of dictionaries containing stock information
        
    Example:
        >>> stocks = get_all_stock(db)
        >>> for item in stocks:
        ...     print(f"{item['name']}: {item['balance']} units ({item['status']})")
    """
    try:
        from models import InventoryLedger, Product
        
        # Aggregate ledger entries by SKU
        ledger_subquery = db.query(
            InventoryLedger.sku,
            func.sum(InventoryLedger.change_qty).label('balance')
        ).group_by(InventoryLedger.sku).subquery()
        
        # Join with products and calculate status
        results = db.query(
            Product.sku,
            Product.name,
            func.coalesce(ledger_subquery.c.balance, 0).label('balance'),
            Product.reorder_point
        ).outerjoin(
            ledger_subquery, Product.sku == ledger_subquery.c.sku
        ).all()
        
        stock_list = []
        for row in results:
            balance = int(row.balance)
            reorder_point = row.reorder_point or 0
            
            # Determine status
            if balance <= 0:
                status = "OUT_OF_STOCK"
            elif balance < reorder_point:
                status = "LOW_STOCK"
            else:
                status = "IN_STOCK"
            
            stock_list.append({
                "sku": row.sku,
                "name": row.name,
                "balance": balance,
                "reorder_point": reorder_point,
                "status": status
            })
        
        return stock_list
        
    except Exception as e:
        logger.error(f"Error fetching all stock levels: {str(e)}")
        raise


def record_sale(db: Session, sale_data: dict) -> Dict:
    """
    Record a sale transaction and update inventory ledger atomically.
    
    Args:
        db: SQLAlchemy database session
        sale_data: Dictionary with keys: sku, quantity, timestamp (optional)
        
    Returns:
        Dictionary with sale record details
        
    Example:
        >>> sale = record_sale(db, {
        ...     "sku": "WIDGET-001",
        ...     "quantity": 5,
        ...     "timestamp": datetime.now()
        ... })
    """
    try:
        from models import Sale, InventoryLedger, Product
        
        # Validate product exists
        product = db.query(Product).filter(Product.sku == sale_data["sku"]).first()
        if not product:
            raise ValueError(f"Product with SKU {sale_data['sku']} not found")
        
        # Validate quantity
        quantity = sale_data.get("quantity", 0)
        if quantity <= 0:
            raise ValueError("Sale quantity must be positive")
        
        # Check if sufficient stock exists
        current_stock = get_current_stock(db, sale_data["sku"])
        if current_stock < quantity:
            raise ValueError(
                f"Insufficient stock for {sale_data['sku']}. "
                f"Available: {current_stock}, Requested: {quantity}"
            )
        
        # Create sale record
        sale = Sale(
            sku=sale_data["sku"],
            quantity=quantity,
            timestamp=sale_data.get("timestamp", datetime.now())
        )
        db.add(sale)
        db.flush()  # Get sale_id
        
        # Calculate new balance
        new_balance = current_stock - quantity
        
        # Create ledger entry (negative for sale)
        ledger_entry = InventoryLedger(
            sku=sale_data["sku"],
            change_qty=-quantity,
            balance_qty=new_balance,
            reason=f"Sale #{sale.sale_id}",
            timestamp=sale.timestamp
        )
        db.add(ledger_entry)
        
        # Commit transaction
        db.commit()
        
        logger.info(f"Sale recorded: SKU {sale_data['sku']}, Qty {quantity}")
        
        return {
            "sale_id": sale.sale_id,
            "sku": sale.sku,
            "quantity": sale.quantity,
            "timestamp": sale.timestamp,
            "new_balance": new_balance
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error recording sale: {str(e)}")
        raise


def adjust_stock(db: Session, sku: str, qty: int, reason: str) -> None:
    """
    Manually adjust stock levels with a ledger entry.
    
    Args:
        db: SQLAlchemy database session
        sku: Product SKU identifier
        qty: Quantity to adjust (positive or negative)
        reason: Reason for adjustment
        
    Example:
        >>> adjust_stock(db, "WIDGET-001", 100, "Initial stock count")
        >>> adjust_stock(db, "WIDGET-001", -5, "Damaged goods")
    """
    try:
        from models import InventoryLedger, Product
        
        # Validate product exists
        product = db.query(Product).filter(Product.sku == sku).first()
        if not product:
            raise ValueError(f"Product with SKU {sku} not found")
        
        # Calculate new balance
        current_stock = get_current_stock(db, sku)
        new_balance = current_stock + qty
        
        if new_balance < 0:
            raise ValueError(
                f"Adjustment would result in negative stock. "
                f"Current: {current_stock}, Adjustment: {qty}"
            )
        
        # Create ledger entry
        ledger_entry = InventoryLedger(
            sku=sku,
            change_qty=qty,
            balance_qty=new_balance,
            reason=reason,
            timestamp=datetime.now()
        )
        db.add(ledger_entry)
        
        # Commit transaction
        db.commit()
        
        logger.info(f"Stock adjusted: SKU {sku}, Change {qty}, Reason: {reason}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error adjusting stock for SKU {sku}: {str(e)}")
        raise


def get_low_stock_items(db: Session, threshold: int = 0) -> List[Dict]:
    """
    Get products with stock below their reorder point.
    
    Args:
        db: SQLAlchemy database session
        threshold: Additional threshold buffer (default: 0)
        
    Returns:
        List of dictionaries with low stock product details
        
    Example:
        >>> low_stock = get_low_stock_items(db, threshold=5)
        >>> print(f"Found {len(low_stock)} items needing reorder")
    """
    try:
        from models import InventoryLedger, Product
        
        # Get all stock levels
        all_stock = get_all_stock(db)
        
        # Filter for low stock items
        low_stock = [
            item for item in all_stock
            if item["balance"] < (item["reorder_point"] + threshold)
        ]
        
        # Sort by urgency (lowest stock first)
        low_stock.sort(key=lambda x: x["balance"] - x["reorder_point"])
        
        logger.info(f"Found {len(low_stock)} low stock items")
        
        return low_stock
        
    except Exception as e:
        logger.error(f"Error fetching low stock items: {str(e)}")
        raise


def calculate_inventory_value(db: Session) -> float:
    """
    Calculate total inventory value based on cost price and current stock.
    
    Args:
        db: SQLAlchemy database session
        
    Returns:
        Total inventory value as float
        
    Example:
        >>> value = calculate_inventory_value(db)
        >>> print(f"Total inventory value: ${value:,.2f}")
    """
    try:
        from models import InventoryLedger, Product
        
        # Aggregate ledger entries by SKU
        ledger_subquery = db.query(
            InventoryLedger.sku,
            func.sum(InventoryLedger.change_qty).label('balance')
        ).group_by(InventoryLedger.sku).subquery()
        
        # Join with products and calculate value
        result = db.query(
            func.sum(
                func.coalesce(ledger_subquery.c.balance, 0) * Product.cost_price
            )
        ).outerjoin(
            ledger_subquery, Product.sku == ledger_subquery.c.sku
        ).scalar()
        
        total_value = float(result) if result is not None else 0.0
        
        logger.info(f"Total inventory value: ${total_value:,.2f}")
        
        return total_value
        
    except Exception as e:
        logger.error(f"Error calculating inventory value: {str(e)}")
        raise