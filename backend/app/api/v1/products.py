"""
Product management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.dependencies import get_db, validate_pagination
from app.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.models import Product

router = APIRouter()


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
    
    Args:
        category: Filter products by category
        search: Search term for product name or SKU
        active: Filter by active/inactive status
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        db: Database session dependency
        
    Returns:
        List[ProductResponse]: List of products matching the criteria
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
    
    Args:
        product: Product data to create
        db: Database session dependency
        
    Returns:
        ProductResponse: Created product with all fields
        
    Raises:
        HTTPException: 400 if SKU already exists
    """
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
    
    # Create new product
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return db_product


@router.get("/products/{sku}", response_model=ProductResponse)
async def get_product(
    sku: str,
    db: Session = Depends(get_db)
) -> ProductResponse:
    """
    Retrieve a single product by SKU.
    
    Args:
        sku: Product SKU identifier
        db: Database session dependency
        
    Returns:
        ProductResponse: Product details
        
    Raises:
        HTTPException: 404 if product not found
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
    
    Args:
        sku: Product SKU identifier
        product_update: Fields to update
        db: Database session dependency
        
    Returns:
        ProductResponse: Updated product
        
    Raises:
        HTTPException: 404 if product not found, 400 for validation errors
    """
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
    
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    
    return db_product


@router.delete("/products/{sku}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    sku: str,
    db: Session = Depends(get_db)
) -> None:
    """
    Soft delete a product by setting active=False.
    
    Args:
        sku: Product SKU identifier
        db: Database session dependency
        
    Raises:
        HTTPException: 404 if product not found
    """
    db_product = db.query(Product).filter(Product.sku == sku).first()
    
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU '{sku}' not found"
        )
    
    db_product.active = False
    db.commit()