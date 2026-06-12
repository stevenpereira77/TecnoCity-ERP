"""
Sale routes - API endpoints for sales management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.sale_service import SaleService
from app.schemas.sale import SaleCreate, SaleResponse
from datetime import datetime
from typing import List

router = APIRouter(prefix="/sales", tags=["sales"])

@router.post("/", response_model=SaleResponse)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    """Create a new sale"""
    try:
        db_sale = SaleService.create_sale(db, sale)
        return db_sale
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[SaleResponse])
def get_sales(skip: int = Query(0), limit: int = Query(100), db: Session = Depends(get_db)):
    """Get all sales"""
    return SaleService.get_all_sales(db, skip, limit)

@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    """Get sale by ID"""
    sale = SaleService.get_sale(db, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale

@router.get("/daily/{date}")
def get_daily_sales(date: str, db: Session = Depends(get_db)):
    """Get sales for a specific day"""
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        sales = SaleService.get_daily_sales(db, date_obj)
        total_sales = SaleService.calculate_daily_sales(db, date_obj)
        total_profit = SaleService.calculate_daily_profit(db, date_obj)
        
        return {
            "date": date,
            "total_sales": total_sales,
            "total_profit": total_profit,
            "number_of_transactions": len(sales),
            "sales": sales,
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format (use YYYY-MM-DD)")

@router.get("/monthly/{year}/{month}")
def get_monthly_sales(year: int, month: int, db: Session = Depends(get_db)):
    """Get sales for a specific month"""
    try:
        total_sales = SaleService.calculate_monthly_sales(db, year, month)
        return {
            "month": f"{year}-{month:02d}",
            "total_sales": total_sales,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
