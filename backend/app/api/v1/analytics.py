"""
Analytics and reporting API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Literal, List
from datetime import datetime, timedelta

from app.dependencies import get_db
from app.schemas import (
    TopProductResponse, 
    RevenueTrendResponse, 
    CategoryBreakdownResponse,
    ABCAnalysisResponse
)
from app.models import Sale, Product

router = APIRouter()


@router.get("/analytics/top-products", response_model=List[TopProductResponse])
async def get_top_products(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    limit: int = Query(10, ge=1, le=50, description="Number of top products to return"),
    sort_by: Literal["revenue", "quantity", "transactions"] = Query("revenue", description="Sort metric"),
    db: Session = Depends(get_db)
) -> List[TopProductResponse]:
    """
    Get top-performing products based on various metrics.
    
    Analyzes sales data over the specified period and ranks products
    by revenue, quantity sold, or number of transactions.
    
    Args:
        days: Analysis period in days
        limit: Number of top products to return
        sort_by: Metric to sort by (revenue, quantity, or transactions)
        db: Database session dependency
        
    Returns:
        List[TopProductResponse]: Top products with performance metrics
    """
    # Calculate date range
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Build query
    query = db.query(
        Sale.sku,
        Product.name,
        Product.category,
        func.sum(Sale.total).label('total_revenue'),
        func.sum(Sale.quantity).label('total_quantity'),
        func.count(Sale.sale_id).label('transaction_count')
    ).join(
        Product, Sale.sku == Product.sku
    ).filter(
        Sale.timestamp >= start_date
    ).group_by(
        Sale.sku,
        Product.name,
        Product.category
    )
    
    # Apply sorting
    if sort_by == "revenue":
        query = query.order_by(desc('total_revenue'))
    elif sort_by == "quantity":
        query = query.order_by(desc('total_quantity'))
    else:  # transactions
        query = query.order_by(desc('transaction_count'))
    
    results = query.limit(limit).all()
    
    # Convert to response model
    top_products = [
        TopProductResponse(
            sku=row.sku,
            name=row.name,
            category=row.category,
            total_revenue=float(row.total_revenue),
            total_quantity=int(row.total_quantity),
            transaction_count=int(row.transaction_count),
            avg_transaction_value=float(row.total_revenue) / int(row.transaction_count)
        )
        for row in results
    ]
    
    return top_products


@router.get("/analytics/revenue-trend", response_model=List[RevenueTrendResponse])
async def get_revenue_trend(
    days: int = Query(90, ge=7, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
) -> List[RevenueTrendResponse]:
    """
    Get daily revenue trend over specified period.
    
    Returns time series data showing daily revenue, useful for
    identifying trends, seasonality, and patterns.
    
    Args:
        days: Analysis period in days
        db: Database session dependency
        
    Returns:
        List[RevenueTrendResponse]: Daily revenue data
    """
    # Calculate date range
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Query daily revenue
    revenue_data = db.query(
        func.date(Sale.timestamp).label('date'),
        func.sum(Sale.total).label('revenue'),
        func.sum(Sale.quantity).label('units_sold'),
        func.count(Sale.sale_id).label('transaction_count')
    ).filter(
        Sale.timestamp >= start_date
    ).group_by(
        func.date(Sale.timestamp)
    ).order_by(
        func.date(Sale.timestamp)
    ).all()
    
    # Convert to response model
    trend = [
        RevenueTrendResponse(
            date=row.date,
            revenue=float(row.revenue),
            units_sold=int(row.units_sold),
            transaction_count=int(row.transaction_count),
            avg_order_value=float(row.revenue) / int(row.transaction_count)
        )
        for row in revenue_data
    ]
    
    return trend


@router.get("/analytics/category-breakdown", response_model=List[CategoryBreakdownResponse])
async def get_category_breakdown(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
) -> List[CategoryBreakdownResponse]:
    """
    Get sales breakdown by product category.
    
    Analyzes performance across different product categories,
    showing revenue, quantity, and market share.
    
    Args:
        days: Analysis period in days
        db: Database session dependency
        
    Returns:
        List[CategoryBreakdownResponse]: Category performance metrics
    """
    # Calculate date range
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Query category performance
    category_data = db.query(
        Product.category,
        func.sum(Sale.total).label('revenue'),
        func.sum(Sale.quantity).label('quantity'),
        func.count(func.distinct(Sale.sku)).label('unique_products'),
        func.count(Sale.sale_id).label('transaction_count')
    ).join(
        Product, Sale.sku == Product.sku
    ).filter(
        Sale.timestamp >= start_date
    ).group_by(
        Product.category
    ).order_by(
        desc('revenue')
    ).all()
    
    # Calculate total revenue for percentage
    total_revenue = sum(float(row.revenue) for row in category_data)
    
    # Convert to response model
    breakdown = [
        CategoryBreakdownResponse(
            category=row.category,
            revenue=float(row.revenue),
            quantity=int(row.quantity),
            unique_products=int(row.unique_products),
            transaction_count=int(row.transaction_count),
            revenue_percentage=round((float(row.revenue) / total_revenue * 100), 2) if total_revenue > 0 else 0
        )
        for row in category_data
    ]
    
    return breakdown


@router.get("/analytics/abc-analysis", response_model=List[ABCAnalysisResponse])
async def get_abc_analysis(
    days: int = Query(90, ge=30, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
) -> List[ABCAnalysisResponse]:
    """
    Perform ABC analysis on inventory.
    
    Classifies products into A, B, C categories based on revenue contribution:
    - A: Top 80% of revenue (typically ~20% of products)
    - B: Next 15% of revenue (typically ~30% of products)
    - C: Remaining 5% of revenue (typically ~50% of products)
    
    Args:
        days: Analysis period in days
        db: Database session dependency
        
    Returns:
        List[ABCAnalysisResponse]: Products with ABC classification
    """
    # Calculate date range
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Query product revenue
    product_revenue = db.query(
        Sale.sku,
        Product.name,
        Product.category,
        func.sum(Sale.total).label('revenue'),
        func.sum(Sale.quantity).label('quantity')
    ).join(
        Product, Sale.sku == Product.sku
    ).filter(
        Sale.timestamp >= start_date
    ).group_by(
        Sale.sku,
        Product.name,
        Product.category
    ).order_by(
        desc('revenue')
    ).all()
    
    if not product_revenue:
        return []
    
    # Calculate total revenue and cumulative percentages
    total_revenue = sum(float(row.revenue) for row in product_revenue)
    
    results = []
    cumulative_revenue = 0
    
    for row in product_revenue:
        revenue = float(row.revenue)
        cumulative_revenue += revenue
        cumulative_percentage = (cumulative_revenue / total_revenue * 100) if total_revenue > 0 else 0
        revenue_percentage = (revenue / total_revenue * 100) if total_revenue > 0 else 0
        
        # Classify into ABC
        if cumulative_percentage <= 80:
            classification = "A"
        elif cumulative_percentage <= 95:
            classification = "B"
        else:
            classification = "C"
        
        results.append(
            ABCAnalysisResponse(
                sku=row.sku,
                name=row.name,
                category=row.category,
                revenue=revenue,
                quantity=int(row.quantity),
                revenue_percentage=round(revenue_percentage, 2),
                cumulative_revenue_percentage=round(cumulative_percentage, 2),
                abc_classification=classification
            )
        )
    
    return results


@router.get("/analytics/summary")
async def get_analytics_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
) -> dict:
    """
    Get comprehensive analytics summary.
    
    Provides high-level KPIs and metrics for the specified period.
    
    Args:
        days: Analysis period in days
        db: Database session dependency
        
    Returns:
        dict: Summary analytics with key metrics
    """
    # Calculate date range
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get overall metrics
    overall = db.query(
        func.sum(Sale.total).label('total_revenue'),
        func.sum(Sale.quantity).label('total_quantity'),
        func.count(Sale.sale_id).label('total_transactions'),
        func.count(func.distinct(Sale.sku)).label('unique_products')
    ).filter(
        Sale.timestamp >= start_date
    ).first()
    
    # Get average order value
    avg_order_value = float(overall.total_revenue) / int(overall.total_transactions) if overall.total_transactions else 0
    
    # Get best selling product
    best_seller = db.query(
        Sale.sku,
        Product.name,
        func.sum(Sale.quantity).label('quantity')
    ).join(
        Product, Sale.sku == Product.sku
    ).filter(
        Sale.timestamp >= start_date
    ).group_by(
        Sale.sku,
        Product.name
    ).order_by(
        desc('quantity')
    ).first()
    
    return {
        "period_days": days,
        "total_revenue": float(overall.total_revenue) if overall.total_revenue else 0,
        "total_units_sold": int(overall.total_quantity) if overall.total_quantity else 0,
        "total_transactions": int(overall.total_transactions) if overall.total_transactions else 0,
        "unique_products_sold": int(overall.unique_products) if overall.unique_products else 0,
        "avg_order_value": round(avg_order_value, 2),
        "avg_daily_revenue": round(float(overall.total_revenue) / days, 2) if overall.total_revenue else 0,
        "best_selling_product": {
            "sku": best_seller.sku,
            "name": best_seller.name,
            "quantity": int(best_seller.quantity)
        } if best_seller else None
    }