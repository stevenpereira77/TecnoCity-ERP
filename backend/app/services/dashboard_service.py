"""
Dashboard service - Business logic for dashboard metrics
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.product import Product
from app.models.sale import Sale, SaleItem
from app.models.purchase import Purchase
from app.models.finance import FinanceRecord, TransactionType, FinancialMetrics
from app.services.sale_service import SaleService
from app.services.purchase_service import PurchaseService
from datetime import datetime, timedelta
from typing import List, Dict, Any

class DashboardService:
    
    @staticmethod
    def get_dashboard_metrics(db: Session) -> Dict[str, Any]:
        """Get all dashboard metrics"""
        today = datetime.utcnow().date()
        today_start = datetime(today.year, today.month, today.day, 0, 0, 0)
        today_end = datetime(today.year, today.month, today.day, 23, 59, 59)
        
        month_start = datetime(today.year, today.month, 1)
        if today.month == 12:
            month_end = datetime(today.year + 1, 1, 1) - timedelta(seconds=1)
        else:
            month_end = datetime(today.year, today.month + 1, 1) - timedelta(seconds=1)
        
        # Basic metrics
        total_products = db.query(func.count(Product.id)).filter(Product.is_active == True).scalar()
        low_stock_products = len(DashboardService.get_low_stock_products(db))
        out_of_stock_products = len(DashboardService.get_out_of_stock_products(db))
        
        # Sales metrics
        daily_sales = SaleService.calculate_daily_sales(db, today)
        monthly_sales = SaleService.calculate_monthly_sales(db, today.year, today.month)
        daily_profit = SaleService.calculate_daily_profit(db, today)
        
        # Count metrics
        products_sold_today = db.query(func.count(SaleItem.id)).join(
            Sale, Sale.id == SaleItem.sale_id
        ).filter(Sale.sale_date >= today_start, Sale.sale_date <= today_end).scalar()
        
        # Financial metrics
        initial_investment = DashboardService.get_initial_investment(db)
        total_sales = DashboardService.get_total_sales(db)
        total_purchases = DashboardService.get_total_purchases(db)
        total_expenses = DashboardService.get_total_expenses(db)
        
        capital_current = FinancialMetrics.calculate_capital(
            initial_investment, total_sales, total_purchases, total_expenses
        )
        
        return {
            "total_products": total_products,
            "products_sold_today": products_sold_today,
            "daily_sales": daily_sales,
            "monthly_sales": monthly_sales,
            "daily_profit": daily_profit,
            "low_stock_products": low_stock_products,
            "out_of_stock_products": out_of_stock_products,
            "initial_investment": initial_investment,
            "capital_current": capital_current,
            "total_sales": total_sales,
            "total_purchases": total_purchases,
        }
    
    @staticmethod
    def get_low_stock_products(db: Session) -> List[Product]:
        """Get products with low stock"""
        return db.query(Product).filter(
            Product.quantity_available <= Product.minimum_stock,
            Product.is_active == True
        ).all()
    
    @staticmethod
    def get_out_of_stock_products(db: Session) -> List[Product]:
        """Get out of stock products"""
        return db.query(Product).filter(
            Product.quantity_available == 0,
            Product.is_active == True
        ).all()
    
    @staticmethod
    def get_top_products(db: Session, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top selling products"""
        results = db.query(
            Product.id,
            Product.code,
            Product.name,
            func.sum(SaleItem.quantity).label('total_quantity'),
            func.sum(SaleItem.total_price).label('total_revenue'),
        ).join(
            SaleItem, Product.id == SaleItem.product_id
        ).group_by(
            Product.id
        ).order_by(
            func.sum(SaleItem.quantity).desc()
        ).limit(limit).all()
        
        return [
            {
                "id": r[0],
                "code": r[1],
                "name": r[2],
                "total_quantity": r[3] or 0,
                "total_revenue": r[4] or 0,
            }
            for r in results
        ]
    
    @staticmethod
    def get_bottom_products(db: Session, limit: int = 5) -> List[Dict[str, Any]]:
        """Get bottom selling products"""
        results = db.query(
            Product.id,
            Product.code,
            Product.name,
            func.sum(SaleItem.quantity).label('total_quantity'),
            func.sum(SaleItem.total_price).label('total_revenue'),
        ).join(
            SaleItem, Product.id == SaleItem.product_id
        ).group_by(
            Product.id
        ).order_by(
            func.sum(SaleItem.quantity).asc()
        ).limit(limit).all()
        
        return [
            {
                "id": r[0],
                "code": r[1],
                "name": r[2],
                "total_quantity": r[3] or 0,
                "total_revenue": r[4] or 0,
            }
            for r in results
        ]
    
    @staticmethod
    def get_sales_by_day(db: Session, days: int = 30) -> List[Dict[str, Any]]:
        """Get sales by day for the last N days"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        results = db.query(
            func.date(Sale.sale_date).label('date'),
            func.sum(Sale.total_amount).label('total_amount'),
            func.sum(Sale.profit).label('total_profit'),
            func.count(Sale.id).label('total_sales'),
        ).filter(
            Sale.sale_date >= start_date
        ).group_by(
            func.date(Sale.sale_date)
        ).order_by(
            func.date(Sale.sale_date)
        ).all()
        
        return [
            {
                "date": str(r[0]),
                "total_amount": r[1] or 0,
                "total_profit": r[2] or 0,
                "total_sales": r[3] or 0,
            }
            for r in results
        ]
    
    @staticmethod
    def get_initial_investment(db: Session) -> float:
        """Get initial investment"""
        record = db.query(func.sum(FinanceRecord.amount)).filter(
            FinanceRecord.transaction_type == TransactionType.INITIAL_INVESTMENT
        ).scalar()
        return record or 0
    
    @staticmethod
    def get_total_sales(db: Session) -> float:
        """Get total sales amount"""
        total = db.query(func.sum(Sale.total_amount)).scalar()
        return total or 0
    
    @staticmethod
    def get_total_purchases(db: Session) -> float:
        """Get total purchases amount"""
        total = db.query(func.sum(Purchase.total_amount)).scalar()
        return total or 0
    
    @staticmethod
    def get_total_expenses(db: Session) -> float:
        """Get total expenses"""
        total = db.query(func.sum(FinanceRecord.amount)).filter(
            FinanceRecord.transaction_type == TransactionType.EXPENSE
        ).scalar()
        return total or 0
    
    @staticmethod
    def get_monthly_sales(db: Session, months: int = 12) -> List[Dict[str, Any]]:
        """Get sales by month"""
        results = []
        for i in range(months):
            target_date = datetime.utcnow() - timedelta(days=30*i)
            total = SaleService.calculate_monthly_sales(db, target_date.year, target_date.month)
            results.append({
                "month": f"{target_date.year}-{target_date.month:02d}",
                "total": total
            })
        return list(reversed(results))
