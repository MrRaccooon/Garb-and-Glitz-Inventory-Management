"""
Suppliers API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.dependencies import get_db
from app.models.suppliers import Supplier
from app.schemas.suppliers import SupplierCreate, SupplierUpdate, SupplierResponse

router = APIRouter()


@router.get("/", response_model=List[SupplierResponse])
async def get_suppliers(
    active_only: bool = Query(True, description="Filter to active suppliers only"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
) -> List[SupplierResponse]:
    """
    Get list of suppliers.

    Args:
        active_only: If True, only return active suppliers
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of suppliers
    """
    query = db.query(Supplier)

    if active_only:
        query = query.filter(Supplier.active == True)

    suppliers = query.offset(skip).limit(limit).all()
    return suppliers


@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: UUID,
    db: Session = Depends(get_db)
) -> SupplierResponse:
    """
    Get a specific supplier by ID.

    Args:
        supplier_id: Supplier UUID
        db: Database session

    Returns:
        Supplier details

    Raises:
        HTTPException: 404 if supplier not found
    """
    supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier with ID {supplier_id} not found"
        )

    return supplier


@router.post("/", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    supplier: SupplierCreate,
    db: Session = Depends(get_db)
) -> SupplierResponse:
    """
    Create a new supplier.

    Args:
        supplier: Supplier data
        db: Database session

    Returns:
        Created supplier
    """
    new_supplier = Supplier(**supplier.model_dump())
    db.add(new_supplier)
    db.commit()
    db.refresh(new_supplier)

    return new_supplier


@router.put("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: UUID,
    supplier_update: SupplierUpdate,
    db: Session = Depends(get_db)
) -> SupplierResponse:
    """
    Update an existing supplier.

    Args:
        supplier_id: Supplier UUID
        supplier_update: Updated supplier data
        db: Database session

    Returns:
        Updated supplier

    Raises:
        HTTPException: 404 if supplier not found
    """
    supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier with ID {supplier_id} not found"
        )

    # Update only provided fields
    update_data = supplier_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(supplier, field, value)

    db.commit()
    db.refresh(supplier)

    return supplier


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(
    supplier_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a supplier.

    Args:
        supplier_id: Supplier UUID
        db: Database session

    Raises:
        HTTPException: 404 if supplier not found
    """
    supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier with ID {supplier_id} not found"
        )

    db.delete(supplier)
    db.commit()
