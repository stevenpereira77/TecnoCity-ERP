"""
Dashboard routes - API endpoints for dashboard metrics
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """Get all dashboard metrics"""
    return DashboardService.get_dashboard_metrics(db)

@router.get("/top-products")
def get_top_products(limit: int = 5, db: Session = Depends(get_db)):
    """Get top selling products"""
    return DashboardService.get_top_products(db, limit)

@router.get("/bottom-products")
def get_bottom_products(limit: int = 5, db: Session = Depends(get_db)):
    """Get bottom selling products"""
    return DashboardService.get_bottom_products(db, limit)

@router.get("/sales-by-day")
def get_sales_by_day(days: int = 30, db: Session = Depends(get_db)):
    """Get sales by day"""
    return DashboardService.get_sales_by_day(db, days)

@router.get("/sales-by-month")
def get_sales_by_month(months: int = 12, db: Session = Depends(get_db)):
    """Get sales by month"""
    return DashboardService.get_sales_by_month(db, months)

@router.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    """Get system alerts"""
    alerts = []
    
    # Low stock alerts
    low_stock = DashboardService.get_low_stock_products(db)
    if low_stock:
        alerts.append({
            "type": "warning",
            "message": f"{len(low_stock)} product(s) with low stock",
            "count": len(low_stock),
        })
    
    # Out of stock alerts
    out_of_stock = DashboardService.get_out_of_stock_products(db)
    if out_of_stock:
        alerts.append({
            "type": "danger",
            "message": f"{len(out_of_stock)} product(s) out of stock",
            "count": len(out_of_stock),
        })
    
    return {"alerts": alerts}
