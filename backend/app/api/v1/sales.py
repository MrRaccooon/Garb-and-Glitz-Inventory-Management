"""
Sales transaction API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime, date
import pandas as pd
import io

from app.dependencies import get_db, validate_pagination
from app.schemas import SaleCreate, SaleResponse
from app.models import Sale, Product, InventoryLedger

router = APIRouter()


@router.post("/sales", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
async def create_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db)
) -> SaleResponse:
    """
    Record a new sale and automatically update inventory ledger.
    
    This endpoint performs a database transaction that:
    1. Validates product exists and has sufficient stock
    2. Creates the sale record
    3. Updates the inventory ledger with the stock reduction
    
    Args:
        sale: Sale data including SKU, quantity, and payment details
        db: Database session dependency
        
    Returns:
        SaleResponse: Created sale record
        
    Raises:
        HTTPException: 404 if product not found, 400 if insufficient stock
    """
    try:
        # Verify product exists
        product = db.query(Product).filter(Product.sku == sale.sku).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with SKU '{sale.sku}' not found"
            )
        
        # Check current stock level
        current_stock = db.query(func.sum(InventoryLedger.change_qty))\
            .filter(InventoryLedger.sku == sale.sku)\
            .scalar() or 0
        
        if current_stock < sale.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Available: {current_stock}, Requested: {sale.quantity}"
            )
        
        # Calculate total
        total = sale.unit_price * sale.quantity
    
        db_sale = Sale(
            timestamp=datetime.utcnow(),
            sku=sale.sku,
            quantity=sale.quantity,
            unit_price=sale.unit_price,
            total=total,
            payment_mode=sale.payment_mode,
            invoice_number=f"INV-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{sale.sku[:4]}"
        )
        db.add(db_sale)
        db.flush()  # Get sale_id without committing
        
        # Update inventory ledger
        new_balance = current_stock - sale.quantity
        ledger_entry = InventoryLedger(
            sku=sale.sku,
            change_qty=-sale.quantity,
            balance_qty=new_balance,
            reason=f"Sale {db_sale.invoice_number}"
        )
        db.add(ledger_entry)
        
        # Commit transaction
        db.commit()
        db.refresh(db_sale)
        
        return db_sale
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing sale: {str(e)}"
        )


@router.post("/sales/bulk", status_code=status.HTTP_201_CREATED)
async def bulk_create_sales(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> dict:
    """
    Bulk upload sales from CSV file.
    
    Expected CSV columns: sku, quantity, unit_price, payment_mode, timestamp (optional)
    
    Args:
        file: CSV file with sales data
        db: Database session dependency
        
    Returns:
        dict: Summary of processed records (success, failed, errors)
        
    Raises:
        HTTPException: 400 for invalid file format or content
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )
    
    try:
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate required columns
        required_columns = {'sku', 'quantity', 'unit_price', 'payment_mode'}
        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {missing}"
            )
        
        success_count = 0
        failed_count = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                # Create sale object
                sale_data = SaleCreate(
                    sku=row['sku'],
                    quantity=int(row['quantity']),
                    unit_price=float(row['unit_price']),
                    payment_mode=row['payment_mode']
                )
                
                # Use the create_sale logic
                product = db.query(Product).filter(Product.sku == sale_data.sku).first()
                if not product:
                    errors.append(f"Row {idx + 2}: Product '{sale_data.sku}' not found")
                    failed_count += 1
                    continue
                
                current_stock = db.query(func.sum(InventoryLedger.change_qty))\
                    .filter(InventoryLedger.sku == sale_data.sku)\
                    .scalar() or 0
                
                if current_stock < sale_data.quantity:
                    errors.append(f"Row {idx + 2}: Insufficient stock for '{sale_data.sku}'")
                    failed_count += 1
                    continue
                
                # Create sale
                total = sale_data.unit_price * sale_data.quantity
                # NEW:
                db_sale = Sale(
                    timestamp=datetime.utcnow(),
                    sku=sale_data.sku,
                    quantity=sale_data.quantity,
                    unit_price=sale_data.unit_price,
                    total=total,
                    payment_mode=sale_data.payment_mode,
                    invoice_number=f"INV-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{idx}"
                )
                db.add(db_sale)
                db.flush()
                
                # Update ledger
                new_balance = current_stock - sale_data.quantity
                ledger_entry = InventoryLedger(
                    sku=sale_data.sku,
                    change_qty=-sale_data.quantity,
                    balance_qty=new_balance,
                    reason=f"Bulk Sale {db_sale.invoice_number}"
                )
                db.add(ledger_entry)
                
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {idx + 2}: {str(e)}")
                failed_count += 1
                continue
        
        # Commit all successful transactions
        db.commit()
        
        return {
            "total_rows": len(df),
            "success": success_count,
            "failed": failed_count,
            "errors": errors[:10]  # Return first 10 errors
        }
        
    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file is empty"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing CSV: {str(e)}"
        )


@router.get("/sales", response_model=List[SaleResponse])
async def list_sales(
    start_date: Optional[date] = Query(None, description="Filter sales from this date"),
    end_date: Optional[date] = Query(None, description="Filter sales until this date"),
    sku: Optional[str] = Query(None, description="Filter by product SKU"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return"),
    db: Session = Depends(get_db)
) -> List[SaleResponse]:
    """
    Retrieve sales records with optional filtering and pagination.
    
    Args:
        start_date: Filter sales from this date (inclusive)
        end_date: Filter sales until this date (inclusive)
        sku: Filter by specific product SKU
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        db: Database session dependency
        
    Returns:
        List[SaleResponse]: List of sales matching the criteria
    """
    skip, limit = validate_pagination(skip, limit)
    
    query = db.query(Sale)
    
    # Apply filters
    if start_date:
        query = query.filter(func.date(Sale.timestamp) >= start_date)
    
    if end_date:
        query = query.filter(func.date(Sale.timestamp) <= end_date)
    
    if sku:
        query = query.filter(Sale.sku == sku)
    
    # Order by timestamp descending
    sales = query.order_by(Sale.timestamp.desc()).offset(skip).limit(limit).all()
    
    return sales


@router.get("/sales/{sale_id}", response_model=SaleResponse)
async def get_sale(
    sale_id: int,
    db: Session = Depends(get_db)
) -> SaleResponse:
    """
    Retrieve a single sale record by ID.
    
    Args:
        sale_id: Sale identifier
        db: Database session dependency
        
    Returns:
        SaleResponse: Sale details
        
    Raises:
        HTTPException: 404 if sale not found
    """
    sale = db.query(Sale).filter(Sale.sale_id == sale_id).first()
    
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sale with ID {sale_id} not found"
        )
    
    return sale