"""
Report routes - API endpoints for report generation
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.report_service import ReportService
from datetime import datetime

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/daily/{date}")
def get_daily_report(date: str, db: Session = Depends(get_db)):
    """Get daily report"""
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        return ReportService.get_daily_report(db, date_obj)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format (use YYYY-MM-DD)")

@router.get("/weekly/{date}")
def get_weekly_report(date: str, db: Session = Depends(get_db)):
    """Get weekly report"""
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        return ReportService.get_weekly_report(db, date_obj)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format (use YYYY-MM-DD)")

@router.get("/monthly/{year}/{month}")
def get_monthly_report(year: int, month: int, db: Session = Depends(get_db)):
    """Get monthly report"""
    try:
        return ReportService.get_monthly_report(db, year, month)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid month")

@router.get("/sales")
def get_sales_report(start_date: str, end_date: str, db: Session = Depends(get_db)):
    """Get sales report"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        return ReportService.generate_sales_report(db, start, end)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format (use YYYY-MM-DD)")

@router.get("/inventory")
def get_inventory_report(db: Session = Depends(get_db)):
    """Get inventory report"""
    return ReportService.generate_inventory_report(db)

@router.get("/profit-loss")
def get_profit_loss_report(start_date: str, end_date: str, db: Session = Depends(get_db)):
    """Get profit & loss report"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        return ReportService.generate_profit_loss_report(db, start, end)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format (use YYYY-MM-DD)")
