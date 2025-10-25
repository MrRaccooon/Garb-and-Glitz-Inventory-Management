"""
Reorder Service Module
Handles reorder point calculations, safety stock, EOQ, and purchase order generation.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import logging
import math
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_reorder_point(db: Session, sku: str) -> float:
    """
    Calculate optimal reorder point based on sales velocity and lead time.
    Formula: (avg_daily_sales × lead_time) + safety_stock
    
    Args:
        db: SQLAlchemy database session
        sku: Product SKU identifier
        
    Returns:
        Calculated reorder point as float
        
    Example:
        >>> reorder_pt = calculate_reorder_point(db, "WIDGET-001")
        >>> print(f"Recommended reorder point: {reorder_pt:.0f} units")
    """
    try:
        from models import Sale, Product
        
        # Get product and lead time
        product = db.query(Product).filter(Product.sku == sku).first()
        if not product:
            raise ValueError(f"Product with SKU {sku} not found")
        
        lead_time = product.lead_time_days or 7  # Default 7 days
        
        # Calculate average daily sales for last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        sales_data = db.query(func.sum(Sale.quantity)).filter(
            and_(
                Sale.sku == sku,
                Sale.timestamp >= thirty_days_ago
            )
        ).scalar()
        
        total_sales = sales_data if sales_data else 0
        avg_daily_sales = total_sales / 30.0
        
        # Calculate safety stock
        safety_stock = calculate_safety_stock(db, sku, service_level=0.95)
        
        # Reorder point formula
        reorder_point = (avg_daily_sales * lead_time) + safety_stock
        
        logger.info(
            f"Reorder point for {sku}: {reorder_point:.2f} "
            f"(avg_daily: {avg_daily_sales:.2f}, lead_time: {lead_time}, "
            f"safety_stock: {safety_stock:.2f})"
        )
        
        return round(reorder_point, 2)
        
    except Exception as e:
        logger.error(f"Error calculating reorder point for {sku}: {str(e)}")
        raise


def calculate_safety_stock(db: Session, sku: str, service_level: float = 0.95) -> float:
    """
    Calculate safety stock using statistical demand variability.
    Formula: z_score × std_dev_daily_sales × sqrt(lead_time)
    
    Args:
        db: SQLAlchemy database session
        sku: Product SKU identifier
        service_level: Desired service level (default: 0.95 = 95%)
        
    Returns:
        Calculated safety stock as float
        
    Example:
        >>> safety = calculate_safety_stock(db, "WIDGET-001", service_level=0.99)
        >>> print(f"Safety stock: {safety:.0f} units")
    """
    try:
        from models import Sale, Product
        
        # Get product and lead time
        product = db.query(Product).filter(Product.sku == sku).first()
        if not product:
            raise ValueError(f"Product with SKU {sku} not found")
        
        lead_time = product.lead_time_days or 7
        
        # Get daily sales for last 60 days
        sixty_days_ago = datetime.now() - timedelta(days=60)
        sales_records = db.query(
            func.date(Sale.timestamp).label('sale_date'),
            func.sum(Sale.quantity).label('daily_qty')
        ).filter(
            and_(
                Sale.sku == sku,
                Sale.timestamp >= sixty_days_ago
            )
        ).group_by(func.date(Sale.timestamp)).all()
        
        if not sales_records or len(sales_records) < 7:
            # Not enough data, use conservative estimate
            logger.warning(f"Insufficient sales data for {sku}, using default safety stock")
            return 10.0
        
        # Extract daily quantities
        daily_quantities = [float(record.daily_qty) for record in sales_records]
        
        # Calculate standard deviation
        if len(daily_quantities) > 1:
            std_dev = statistics.stdev(daily_quantities)
        else:
            std_dev = daily_quantities[0] * 0.5  # 50% of single data point
        
        # Z-scores for common service levels
        z_scores = {
            0.90: 1.28,
            0.95: 1.65,
            0.99: 2.33
        }
        z_score = z_scores.get(service_level, 1.65)
        
        # Safety stock formula
        safety_stock = z_score * std_dev * math.sqrt(lead_time)
        
        logger.info(
            f"Safety stock for {sku}: {safety_stock:.2f} "
            f"(std_dev: {std_dev:.2f}, z_score: {z_score}, lead_time: {lead_time})"
        )
        
        return round(safety_stock, 2)
        
    except Exception as e:
        logger.error(f"Error calculating safety stock for {sku}: {str(e)}")
        raise


def get_reorder_suggestions(db: Session) -> List[Dict]:
    """
    Generate reorder suggestions for all low stock items with supplier info.
    
    Args:
        db: SQLAlchemy database session
        
    Returns:
        List of dictionaries with reorder suggestions
        
    Example:
        >>> suggestions = get_reorder_suggestions(db)
        >>> for item in suggestions:
        ...     print(f"Reorder {item['suggested_qty']} units of {item['name']}")
    """
    try:
        from services.inventory_service import get_low_stock_items, get_current_stock
        from models import Product
        
        # Get low stock items
        low_stock = get_low_stock_items(db)
        
        suggestions = []
        for item in low_stock:
            sku = item["sku"]
            
            # Get product details
            product = db.query(Product).filter(Product.sku == sku).first()
            if not product:
                continue
            
            current_stock = item["balance"]
            
            # Calculate optimal reorder point
            optimal_reorder_point = calculate_reorder_point(db, sku)
            
            # Calculate suggested order quantity
            # Order enough to reach 2x reorder point or minimum EOQ
            try:
                eoq = calculate_economic_order_qty(db, sku)
                suggested_qty = max(
                    int(optimal_reorder_point * 2 - current_stock),
                    eoq
                )
            except:
                # Fallback if EOQ calculation fails
                suggested_qty = int(optimal_reorder_point * 2 - current_stock)
            
            suggestion = {
                "sku": sku,
                "name": item["name"],
                "current_stock": current_stock,
                "reorder_point": item["reorder_point"],
                "optimal_reorder_point": round(optimal_reorder_point, 2),
                "suggested_qty": max(suggested_qty, 1),
                "supplier_id": None,  # Would need Supplier model
                "supplier_name": None  # Would need Supplier model
            }
            
            suggestions.append(suggestion)
        
        logger.info(f"Generated {len(suggestions)} reorder suggestions")
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Error generating reorder suggestions: {str(e)}")
        raise


def calculate_economic_order_qty(
    db: Session, 
    sku: str, 
    holding_cost_pct: float = 0.2
) -> int:
    """
    Calculate Economic Order Quantity (EOQ) for optimal order size.
    Formula: sqrt((2 × annual_demand × order_cost) / (unit_cost × holding_cost_pct))
    
    Args:
        db: SQLAlchemy database session
        sku: Product SKU identifier
        holding_cost_pct: Annual holding cost as percentage of unit cost (default: 0.2 = 20%)
        
    Returns:
        Calculated EOQ as integer
        
    Example:
        >>> eoq = calculate_economic_order_qty(db, "WIDGET-001", holding_cost_pct=0.25)
        >>> print(f"Economic order quantity: {eoq} units")
    """
    try:
        from models import Sale, Product
        
        # Get product details
        product = db.query(Product).filter(Product.sku == sku).first()
        if not product:
            raise ValueError(f"Product with SKU {sku} not found")
        
        unit_cost = product.cost_price
        
        # Calculate annual demand based on last 90 days
        ninety_days_ago = datetime.now() - timedelta(days=90)
        sales_90d = db.query(func.sum(Sale.quantity)).filter(
            and_(
                Sale.sku == sku,
                Sale.timestamp >= ninety_days_ago
            )
        ).scalar()
        
        sales_90d = sales_90d if sales_90d else 0
        annual_demand = (sales_90d / 90.0) * 365.0
        
        if annual_demand == 0:
            logger.warning(f"No sales data for {sku}, using minimum order quantity")
            return 10
        
        # Estimate order cost (fixed cost per order)
        # This should ideally come from configuration or supplier data
        order_cost = 50.0  # Default $50 per order
        
        # Calculate holding cost per unit per year
        holding_cost_per_unit = unit_cost * holding_cost_pct
        
        # EOQ formula
        if holding_cost_per_unit > 0:
            eoq = math.sqrt(
                (2 * annual_demand * order_cost) / holding_cost_per_unit
            )
        else:
            eoq = annual_demand / 12  # Monthly supply if no holding cost
        
        eoq_int = max(int(round(eoq)), 1)
        
        logger.info(
            f"EOQ for {sku}: {eoq_int} units "
            f"(annual_demand: {annual_demand:.0f}, unit_cost: ${unit_cost:.2f})"
        )
        
        return eoq_int
        
    except Exception as e:
        logger.error(f"Error calculating EOQ for {sku}: {str(e)}")
        raise


def generate_purchase_order(
    db: Session, 
    supplier_id: int, 
    items: List[dict]
) -> Dict:
    """
    Generate a purchase order for multiple items from a supplier.
    
    Args:
        db: SQLAlchemy database session
        supplier_id: Supplier identifier
        items: List of dicts with keys: sku, qty_ordered
        
    Returns:
        Dictionary with PO details
        
    Example:
        >>> po = generate_purchase_order(db, supplier_id=123, items=[
        ...     {"sku": "WIDGET-001", "qty_ordered": 100},
        ...     {"sku": "WIDGET-002", "qty_ordered": 50}
        ... ])
        >>> print(f"PO created: #{po['po_id']}")
    """
    try:
        from models import PurchaseOrder, Product
        
        if not items:
            raise ValueError("Cannot create purchase order with no items")
        
        # Validate all SKUs exist
        for item in items:
            product = db.query(Product).filter(
                Product.sku == item["sku"]
            ).first()
            if not product:
                raise ValueError(f"Product with SKU {item['sku']} not found")
            
            if item.get("qty_ordered", 0) <= 0:
                raise ValueError(f"Invalid quantity for SKU {item['sku']}")
        
        # Create purchase orders (one per line item in this model structure)
        po_records = []
        for item in items:
            po = PurchaseOrder(
                supplier_id=supplier_id,
                sku=item["sku"],
                qty_ordered=item["qty_ordered"],
                status="PENDING"
            )
            db.add(po)
            db.flush()
            po_records.append(po)
        
        # Commit transaction
        db.commit()
        
        po_ids = [po.po_id for po in po_records]
        
        logger.info(
            f"Purchase order created: Supplier {supplier_id}, "
            f"Items: {len(items)}, PO IDs: {po_ids}"
        )
        
        return {
            "po_ids": po_ids,
            "supplier_id": supplier_id,
            "items": items,
            "status": "PENDING",
            "created_at": datetime.now()
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error generating purchase order: {str(e)}")
        raise