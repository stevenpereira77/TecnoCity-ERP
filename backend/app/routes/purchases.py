"""
Purchase routes - API endpoints for purchase management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.purchase_service import PurchaseService
from app.schemas.purchase import PurchaseCreate, PurchaseResponse
from typing import List

router = APIRouter(prefix="/purchases", tags=["purchases"])

@router.post("/", response_model=PurchaseResponse)
def create_purchase(purchase: PurchaseCreate, db: Session = Depends(get_db)):
    """Create a new purchase"""
    try:
        db_purchase = PurchaseService.create_purchase(db, purchase)
        return db_purchase
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[PurchaseResponse])
def get_purchases(skip: int = Query(0), limit: int = Query(100), db: Session = Depends(get_db)):
    """Get all purchases"""
    return PurchaseService.get_all_purchases(db, skip, limit)

@router.get("/{purchase_id}", response_model=PurchaseResponse)
def get_purchase(purchase_id: int, db: Session = Depends(get_db)):
    """Get purchase by ID"""
    purchase = PurchaseService.get_purchase(db, purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return purchase

@router.put("/{purchase_id}/receive")
def mark_purchase_received(purchase_id: int, db: Session = Depends(get_db)):
    """Mark purchase as received"""
    purchase = PurchaseService.mark_received(db, purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return {"message": "Purchase marked as received", "purchase": purchase}
