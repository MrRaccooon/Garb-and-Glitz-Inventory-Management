"""
Product management API endpoints - FIXED VERSION
File: backend/app/api/v1/products.py
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import Optional, List
import logging

from app.dependencies import get_db, validate_pagination
from app.schemas.products import ProductCreate, ProductUpdate, ProductResponse
from app.models.products import Product

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/products", response_model=List[ProductResponse])
async def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in name or SKU"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return"),
    db: Session = Depends(get_db)
) -> List[ProductResponse]:
    """
    Retrieve a list of products with optional filtering and pagination.
    """
    skip, limit = validate_pagination(skip, limit)
    
    query = db.query(Product)
    
    # Apply filters
    if category:
        query = query.filter(Product.category == category)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_pattern)) | 
            (Product.sku.ilike(search_pattern))
        )
    
    if active is not None:
        query = query.filter(Product.active == active)
    
    # Apply pagination and execute
    products = query.offset(skip).limit(limit).all()
    
    return products


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
) -> ProductResponse:
    """
    Create a new product in the inventory.
    """
    try:
        # Check if SKU already exists
        existing = db.query(Product).filter(Product.sku == product.sku).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with SKU '{product.sku}' already exists"
            )
        
        # Validate business logic
        if product.sell_price < product.cost_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sell price cannot be less than cost price"
            )
        
        # ✅ FIXED: Validate supplier_id if provided
        if product.supplier_id:
            from app.models.suppliers import Supplier
            supplier = db.query(Supplier).filter(Supplier.supplier_id == product.supplier_id).first()
            if not supplier:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Supplier with ID '{product.supplier_id}' not found"
                )
        
        # Create new product
        db_product = Product(**product.model_dump())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        
        logger.info(f"Product created successfully: {db_product.sku}")
        return db_product
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database constraint violation. Please check all required fields."
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/products/{sku}", response_model=ProductResponse)
async def get_product(
    sku: str,
    db: Session = Depends(get_db)
) -> ProductResponse:
    """
    Retrieve a single product by SKU.
    """
    product = db.query(Product).filter(Product.sku == sku).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU '{sku}' not found"
        )
    
    return product


@router.put("/products/{sku}", response_model=ProductResponse)
async def update_product(
    sku: str,
    product_update: ProductUpdate,
    db: Session = Depends(get_db)
) -> ProductResponse:
    """
    Update an existing product.
    """
    try:
        db_product = db.query(Product).filter(Product.sku == sku).first()
        
        if not db_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with SKU '{sku}' not found"
            )
        
        # Update only provided fields
        update_data = product_update.model_dump(exclude_unset=True)
        
        # Validate business logic if prices are being updated
        cost_price = update_data.get("cost_price", db_product.cost_price)
        sell_price = update_data.get("sell_price", db_product.sell_price)
        
        if sell_price < cost_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sell price cannot be less than cost price"
            )
        
        # ✅ FIXED: Validate supplier_id if being updated
        if "supplier_id" in update_data and update_data["supplier_id"]:
            from app.models.suppliers import Supplier
            supplier = db.query(Supplier).filter(Supplier.supplier_id == update_data["supplier_id"]).first()
            if not supplier:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Supplier with ID '{update_data['supplier_id']}' not found"
                )
        
        for field, value in update_data.items():
            setattr(db_product, field, value)
        
        db.commit()
        db.refresh(db_product)
        
        logger.info(f"Product updated successfully: {sku}")
        return db_product
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database constraint violation. Please check all required fields."
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.delete("/products/{sku}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    sku: str,
    db: Session = Depends(get_db)
) -> None:
    """
    Soft delete a product by setting active=False.
    """
    db_product = db.query(Product).filter(Product.sku == sku).first()
    
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU '{sku}' not found"
        )
    
    db_product.active = False
    db.commit()
    logger.info(f"Product soft deleted: {sku}")