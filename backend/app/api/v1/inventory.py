"""
Inventory management and tracking API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.dependencies import get_db, validate_pagination
from app.schemas import InventoryAdjust, InventoryResponse, LedgerEntryResponse
from app.models import Product, InventoryLedger

router = APIRouter()


@router.get("/inventory", response_model=List[InventoryResponse])
async def get_current_inventory(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return"),
    db: Session = Depends(get_db)
) -> List[InventoryResponse]:
    """
    Get current stock levels for all products.
    
    This endpoint aggregates the inventory ledger to calculate current
    balance for each product and joins with product information.
    
    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        db: Database session dependency
        
    Returns:
        List[InventoryResponse]: Current inventory status for all products
    """
    skip, limit = validate_pagination(skip, limit)
    
    # Aggregate inventory ledger to get current balance
    inventory_query = db.query(
        Product.sku,
        Product.name,
        Product.category,
        Product.reorder_point,
        func.coalesce(func.sum(InventoryLedger.change_qty), 0).label('balance_qty')
    ).outerjoin(
        InventoryLedger, Product.sku == InventoryLedger.sku
    ).filter(
        Product.active == True
    ).group_by(
        Product.sku,
        Product.name,
        Product.category,
        Product.reorder_point
    ).offset(skip).limit(limit)
    
    results = inventory_query.all()
    
    # Convert to response model
    inventory = [
        InventoryResponse(
            sku=row.sku,
            name=row.name,
            category=row.category,
            balance_qty=row.balance_qty,
            reorder_point=row.reorder_point,
            needs_reorder=row.balance_qty < row.reorder_point
        )
        for row in results
    ]
    
    return inventory


@router.post("/inventory/adjust", response_model=LedgerEntryResponse, status_code=status.HTTP_201_CREATED)
async def adjust_inventory(
    adjustment: InventoryAdjust,
    db: Session = Depends(get_db)
) -> LedgerEntryResponse:
    """
    Manually adjust inventory levels with reason.
    
    Use this endpoint for stock corrections, returns, damages, or other
    manual adjustments that don't come from sales or purchases.
    
    Args:
        adjustment: Adjustment details including SKU, quantity change, and reason
        db: Database session dependency
        
    Returns:
        LedgerEntryResponse: Created ledger entry
        
    Raises:
        HTTPException: 404 if product not found, 400 for invalid adjustment
    """
    # Verify product exists
    product = db.query(Product).filter(Product.sku == adjustment.sku).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU '{adjustment.sku}' not found"
        )
    
    # Calculate current balance
    current_balance = db.query(func.coalesce(func.sum(InventoryLedger.change_qty), 0))\
        .filter(InventoryLedger.sku == adjustment.sku)\
        .scalar()
    
    new_balance = current_balance + adjustment.change_qty
    
    # Prevent negative inventory
    if new_balance < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Adjustment would result in negative inventory. Current: {current_balance}, Change: {adjustment.change_qty}"
        )
    
    # Create ledger entry
    ledger_entry = InventoryLedger(
        sku=adjustment.sku,
        change_qty=adjustment.change_qty,
        balance_qty=new_balance,
        reason=adjustment.reason
    )
    
    db.add(ledger_entry)
    db.commit()
    db.refresh(ledger_entry)
    
    return ledger_entry


@router.get("/inventory/ledger/{sku}", response_model=List[LedgerEntryResponse])
async def get_inventory_ledger(
    sku: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return"),
    db: Session = Depends(get_db)
) -> List[LedgerEntryResponse]:
    """
    Get transaction history for a specific product.
    
    Returns all inventory movements (sales, adjustments, receipts) for
    the specified SKU in reverse chronological order.
    
    Args:
        sku: Product SKU identifier
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        db: Database session dependency
        
    Returns:
        List[LedgerEntryResponse]: Inventory transaction history
        
    Raises:
        HTTPException: 404 if product not found
    """
    skip, limit = validate_pagination(skip, limit)
    
    # Verify product exists
    product = db.query(Product).filter(Product.sku == sku).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU '{sku}' not found"
        )
    
    # Get ledger entries
    ledger_entries = db.query(InventoryLedger)\
        .filter(InventoryLedger.sku == sku)\
        .order_by(InventoryLedger.transaction_id.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return ledger_entries


@router.get("/inventory/low-stock", response_model=List[InventoryResponse])
async def get_low_stock_items(
    db: Session = Depends(get_db)
) -> List[InventoryResponse]:
    """
    Get all products where current stock is below reorder point.
    
    This endpoint identifies products that need to be reordered based on
    their current stock level versus their configured reorder point.
    
    Args:
        db: Database session dependency
        
    Returns:
        List[InventoryResponse]: Products needing reorder, sorted by urgency
    """
    # Get current inventory with balance below reorder point
    low_stock_query = db.query(
        Product.sku,
        Product.name,
        Product.category,
        Product.reorder_point,
        func.coalesce(func.sum(InventoryLedger.change_qty), 0).label('balance_qty')
    ).outerjoin(
        InventoryLedger, Product.sku == InventoryLedger.sku
    ).filter(
        Product.active == True
    ).group_by(
        Product.sku,
        Product.name,
        Product.category,
        Product.reorder_point
    ).having(
        func.coalesce(func.sum(InventoryLedger.change_qty), 0) < Product.reorder_point
    ).order_by(
        (func.coalesce(func.sum(InventoryLedger.change_qty), 0) - Product.reorder_point).asc()
    )
    
    results = low_stock_query.all()
    
    # Convert to response model
    low_stock = [
        InventoryResponse(
            sku=row.sku,
            name=row.name,
            category=row.category,
            balance_qty=row.balance_qty,
            reorder_point=row.reorder_point,
            needs_reorder=True
        )
        for row in results
    ]
    
    return low_stock