"""
Analytics Service Module
Provides business intelligence functions for inventory and sales analysis.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_top_products(
    db: Session, 
    days: int = 30, 
    limit: int = 10, 
    sort_by: str = "revenue"
) -> List[Dict]:
    """
    Get top performing products by revenue or quantity sold.
    
    Args:
        db: SQLAlchemy database session
        days: Number of days to analyze (default: 30)
        limit: Maximum number of products to return (default: 10)
        sort_by: Sort criteria - "revenue" or "quantity" (default: "revenue")
        
    Returns:
        List of dictionaries with product performance metrics
        
    Example:
        >>> top = get_top_products(db, days=90, limit=5, sort_by="revenue")
        >>> for idx, product in enumerate(top, 1):
        ...     print(f"{idx}. {product['name']}: ${product['revenue']:,.2f}")
    """
    try:
        from models import Sale, Product
        
        # Calculate date range
        start_date = datetime.now() - timedelta(days=days)
        
        # Query sales with product details
        query = db.query(
            Sale.sku,
            Product.name,
            Product.sell_price,
            func.sum(Sale.quantity).label('total_quantity'),
            func.count(Sale.sale_id).label('transaction_count')
        ).join(
            Product, Sale.sku == Product.sku
        ).filter(
            Sale.timestamp >= start_date
        ).group_by(
            Sale.sku, Product.name, Product.sell_price
        )
        
        results = query.all()
        
        # Calculate metrics
        products = []
        for row in results:
            revenue = float(row.total_quantity) * float(row.sell_price)
            products.append({
                "sku": row.sku,
                "name": row.name,
                "quantity_sold": int(row.total_quantity),
                "transaction_count": int(row.transaction_count),
                "revenue": round(revenue, 2),
                "avg_price": float(row.sell_price)
            })
        
        # Sort by specified criteria
        if sort_by == "quantity":
            products.sort(key=lambda x: x["quantity_sold"], reverse=True)
        else:  # Default to revenue
            products.sort(key=lambda x: x["revenue"], reverse=True)
        
        top_products = products[:limit]
        
        logger.info(
            f"Retrieved top {len(top_products)} products "
            f"(last {days} days, sorted by {sort_by})"
        )
        
        return top_products
        
    except Exception as e:
        logger.error(f"Error fetching top products: {str(e)}")
        raise


def abc_analysis(db: Session) -> Dict:
    """
    Perform ABC analysis to classify inventory by value.
    A: Top 20% of products by value (typically 80% of total value)
    B: Next 30% of products (typically 15% of total value)
    C: Remaining 50% of products (typically 5% of total value)
    
    Args:
        db: SQLAlchemy database session
        
    Returns:
        Dictionary with classification results
        
    Example:
        >>> analysis = abc_analysis(db)
        >>> print(f"Class A: {len(analysis['A'])} products")
        >>> print(f"Class B: {len(analysis['B'])} products")
        >>> print(f"Class C: {len(analysis['C'])} products")
    """
    try:
        from models import InventoryLedger, Product
        
        # Get current stock levels with product details
        ledger_subquery = db.query(
            InventoryLedger.sku,
            func.sum(InventoryLedger.change_qty).label('balance')
        ).group_by(InventoryLedger.sku).subquery()
        
        results = db.query(
            Product.sku,
            Product.name,
            Product.cost_price,
            func.coalesce(ledger_subquery.c.balance, 0).label('balance')
        ).outerjoin(
            ledger_subquery, Product.sku == ledger_subquery.c.sku
        ).all()
        
        # Calculate inventory value for each product
        products = []
        total_value = 0.0
        
        for row in results:
            balance = float(row.balance)
            cost_price = float(row.cost_price)
            value = balance * cost_price
            total_value += value
            
            products.append({
                "sku": row.sku,
                "name": row.name,
                "quantity": int(balance),
                "cost_price": cost_price,
                "inventory_value": round(value, 2)
            })
        
        # Sort by inventory value descending
        products.sort(key=lambda x: x["inventory_value"], reverse=True)
        
        # Calculate cumulative percentages
        cumulative_value = 0.0
        for product in products:
            cumulative_value += product["inventory_value"]
            product["cumulative_pct"] = (
                (cumulative_value / total_value * 100) if total_value > 0 else 0
            )
        
        # Classify products
        classification = {
            "A": [],
            "B": [],
            "C": [],
            "summary": {
                "total_value": round(total_value, 2),
                "total_products": len(products)
            }
        }
        
        for product in products:
            cum_pct = product["cumulative_pct"]
            
            if cum_pct <= 80:
                product["class"] = "A"
                classification["A"].append(product)
            elif cum_pct <= 95:
                product["class"] = "B"
                classification["B"].append(product)
            else:
                product["class"] = "C"
                classification["C"].append(product)
        
        # Add summary statistics
        classification["summary"]["A_count"] = len(classification["A"])
        classification["summary"]["B_count"] = len(classification["B"])
        classification["summary"]["C_count"] = len(classification["C"])
        
        if classification["A"]:
            classification["summary"]["A_value"] = round(
                sum(p["inventory_value"] for p in classification["A"]), 2
            )
            classification["summary"]["A_value_pct"] = round(
                (classification["summary"]["A_value"] / total_value * 100) if total_value > 0 else 0, 2
            )
        
        logger.info(
            f"ABC Analysis: A={len(classification['A'])}, "
            f"B={len(classification['B'])}, C={len(classification['C'])}"
        )
        
        return classification
        
    except Exception as e:
        logger.error(f"Error performing ABC analysis: {str(e)}")
        raise


def calculate_inventory_turnover(db: Session, days: int = 365) -> float:
    """
    Calculate inventory turnover ratio.
    Formula: COGS / Average Inventory Value
    
    Args:
        db: SQLAlchemy database session
        days: Period for calculation (default: 365 for annual)
        
    Returns:
        Inventory turnover ratio as float
        
    Example:
        >>> turnover = calculate_inventory_turnover(db, days=365)
        >>> print(f"Annual inventory turnover: {turnover:.2f}x")
    """
    try:
        from models import Sale, Product
        from services.inventory_service import calculate_inventory_value
        
        # Calculate COGS (Cost of Goods Sold) for the period
        start_date = datetime.now() - timedelta(days=days)
        
        sales_query = db.query(
            Sale.sku,
            func.sum(Sale.quantity).label('quantity_sold')
        ).filter(
            Sale.timestamp >= start_date
        ).group_by(Sale.sku).subquery()
        
        cogs_result = db.query(
            func.sum(sales_query.c.quantity_sold * Product.cost_price)
        ).join(
            Product, sales_query.c.sku == Product.sku
        ).scalar()
        
        cogs = float(cogs_result) if cogs_result else 0.0
        
        # Get current inventory value
        current_inventory_value = calculate_inventory_value(db)
        
        # For average inventory, we'll use current value
        # (Ideally would track historical values)
        avg_inventory_value = current_inventory_value
        
        if avg_inventory_value > 0:
            turnover = cogs / avg_inventory_value
        else:
            turnover = 0.0
        
        logger.info(
            f"Inventory turnover ({days} days): {turnover:.2f}x "
            f"(COGS: ${cogs:,.2f}, Avg Inventory: ${avg_inventory_value:,.2f})"
        )
        
        return round(turnover, 2)
        
    except Exception as e:
        logger.error(f"Error calculating inventory turnover: {str(e)}")
        raise


def get_sales_velocity(db: Session, sku: str, days: int = 30) -> float:
    """
    Calculate average daily sales velocity for a product.
    
    Args:
        db: SQLAlchemy database session
        sku: Product SKU identifier
        days: Period for calculation (default: 30)
        
    Returns:
        Units sold per day as float
        
    Example:
        >>> velocity = get_sales_velocity(db, "WIDGET-001", days=30)
        >>> print(f"Selling {velocity:.1f} units per day")
    """
    try:
        from models import Sale
        
        start_date = datetime.now() - timedelta(days=days)
        
        total_sales = db.query(func.sum(Sale.quantity)).filter(
            and_(
                Sale.sku == sku,
                Sale.timestamp >= start_date
            )
        ).scalar()
        
        total_sales = total_sales if total_sales else 0
        velocity = float(total_sales) / float(days)
        
        logger.info(f"Sales velocity for {sku}: {velocity:.2f} units/day")
        
        return round(velocity, 2)
        
    except Exception as e:
        logger.error(f"Error calculating sales velocity for {sku}: {str(e)}")
        raise


def get_revenue_trend(db: Session, days: int = 90) -> List[Dict]:
    """
    Get daily revenue trend for specified period.
    
    Args:
        db: SQLAlchemy database session
        days: Number of days to analyze (default: 90)
        
    Returns:
        List of dictionaries with daily revenue data
        
    Example:
        >>> trend = get_revenue_trend(db, days=30)
        >>> for day in trend[-7:]:  # Last 7 days
        ...     print(f"{day['date']}: ${day['revenue']:,.2f}")
    """
    try:
        from models import Sale, Product
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Query daily sales with revenue calculation
        results = db.query(
            func.date(Sale.timestamp).label('sale_date'),
            func.sum(Sale.quantity * Product.sell_price).label('daily_revenue'),
            func.sum(Sale.quantity).label('daily_quantity')
        ).join(
            Product, Sale.sku == Product.sku
        ).filter(
            Sale.timestamp >= start_date
        ).group_by(
            func.date(Sale.timestamp)
        ).order_by(
            func.date(Sale.timestamp)
        ).all()
        
        # Convert to list of dicts
        trend_data = []
        for row in results:
            trend_data.append({
                "date": row.sale_date.isoformat() if hasattr(row.sale_date, 'isoformat') else str(row.sale_date),
                "revenue": round(float(row.daily_revenue), 2),
                "quantity": int(row.daily_quantity)
            })
        
        # Fill in missing days with zero revenue
        date_dict = {item["date"]: item for item in trend_data}
        complete_trend = []
        
        current_date = start_date.date()
        end_date = datetime.now().date()
        
        while current_date <= end_date:
            date_str = current_date.isoformat()
            if date_str in date_dict:
                complete_trend.append(date_dict[date_str])
            else:
                complete_trend.append({
                    "date": date_str,
                    "revenue": 0.0,
                    "quantity": 0
                })
            current_date += timedelta(days=1)
        
        logger.info(f"Retrieved revenue trend for {len(complete_trend)} days")
        
        return complete_trend
        
    except Exception as e:
        logger.error(f"Error fetching revenue trend: {str(e)}")
        raise


def get_category_breakdown(db: Session) -> List[Dict]:
    """
    Get sales breakdown by product category.
    Note: Assumes Product model has a 'category' field.
    If not available, returns aggregated data without categories.
    
    Args:
        db: SQLAlchemy database session
        
    Returns:
        List of dictionaries with category performance
        
    Example:
        >>> breakdown = get_category_breakdown(db)
        >>> for cat in breakdown:
        ...     print(f"{cat['category']}: ${cat['revenue']:,.2f}")
    """
    try:
        from models import Sale, Product
        
        # Check if Product has category field
        try:
            # Attempt category-based query
            results = db.query(
                Product.category,
                func.sum(Sale.quantity).label('total_quantity'),
                func.sum(Sale.quantity * Product.sell_price).label('total_revenue'),
                func.count(func.distinct(Sale.sku)).label('product_count')
            ).join(
                Product, Sale.sku == Product.sku
            ).group_by(
                Product.category
            ).all()
            
            breakdown = []
            for row in results:
                breakdown.append({
                    "category": row.category or "Uncategorized",
                    "quantity_sold": int(row.total_quantity),
                    "revenue": round(float(row.total_revenue), 2),
                    "product_count": int(row.product_count)
                })
            
        except AttributeError:
            # If category field doesn't exist, return aggregate data
            logger.warning("Product model has no 'category' field, returning aggregate data")
            
            result = db.query(
                func.sum(Sale.quantity).label('total_quantity'),
                func.sum(Sale.quantity * Product.sell_price).label('total_revenue'),
                func.count(func.distinct(Sale.sku)).label('product_count')
            ).join(
                Product, Sale.sku == Product.sku
            ).first()
            
            breakdown = [{
                "category": "All Products",
                "quantity_sold": int(result.total_quantity) if result.total_quantity else 0,
                "revenue": round(float(result.total_revenue), 2) if result.total_revenue else 0.0,
                "product_count": int(result.product_count) if result.product_count else 0
            }]
        
        # Sort by revenue descending
        breakdown.sort(key=lambda x: x["revenue"], reverse=True)
        
        logger.info(f"Category breakdown: {len(breakdown)} categories")
        
        return breakdown
        
    except Exception as e:
        logger.error(f"Error fetching category breakdown: {str(e)}")
        raise