"""
Report service - Generate reports in multiple formats
"""
from sqlalchemy.orm import Session
from app.models.sale import Sale, SaleItem
from app.models.purchase import Purchase, PurchaseItem
from app.models.product import Product
from datetime import datetime, timedelta
from typing import List, Dict, Any
import csv
import io

class ReportService:
    
    @staticmethod
    def generate_sales_report(db: Session, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Generate sales report"""
        sales = db.query(Sale).filter(
            Sale.sale_date >= start_date,
            Sale.sale_date <= end_date
        ).all()
        
        report_data = []
        for sale in sales:
            report_data.append({
                "sale_number": sale.sale_number,
                "date": sale.sale_date.strftime("%Y-%m-%d %H:%M:%S"),
                "customer": sale.customer.name if sale.customer else "Walk-in",
                "total_amount": sale.total_amount,
                "profit": sale.profit,
                "profit_margin": sale.profit_margin_percent,
                "payment_method": sale.payment_method,
                "items_count": len(sale.items),
            })
        
        return report_data
    
    @staticmethod
    def generate_inventory_report(db: Session) -> List[Dict[str, Any]]:
        """Generate inventory report"""
        products = db.query(Product).filter(Product.is_active == True).all()
        
        report_data = []
        for product in products:
            report_data.append({
                "code": product.code,
                "name": product.name,
                "category": product.category,
                "quantity_available": product.quantity_available,
                "minimum_stock": product.minimum_stock,
                "purchase_price": product.purchase_price,
                "selling_price": product.selling_price,
                "profit_per_unit": product.profit_per_unit,
                "status": "Out of Stock" if product.is_out_of_stock else ("Low Stock" if product.is_low_stock else "OK"),
            })
        
        return report_data
    
    @staticmethod
    def generate_profit_loss_report(db: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate profit & loss report"""
        sales = db.query(Sale).filter(
            Sale.sale_date >= start_date,
            Sale.sale_date <= end_date
        ).all()
        
        total_revenue = sum(sale.total_amount for sale in sales)
        total_cost = sum(sale.cost_of_goods for sale in sales)
        total_profit = sum(sale.profit for sale in sales)
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            "period": f"{start_date.date()} to {end_date.date()}",
            "total_revenue": total_revenue,
            "total_cost": total_cost,
            "total_profit": total_profit,
            "profit_margin_percent": profit_margin,
            "number_of_sales": len(sales),
        }
    
    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], filename: str) -> str:
        """Export data to CSV format"""
        if not data:
            return ""
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()
    
    @staticmethod
    def get_daily_report(db: Session, date: datetime) -> Dict[str, Any]:
        """Get daily report"""
        start = datetime(date.year, date.month, date.day, 0, 0, 0)
        end = datetime(date.year, date.month, date.day, 23, 59, 59)
        
        sales = db.query(Sale).filter(
            Sale.sale_date >= start,
            Sale.sale_date <= end
        ).all()
        
        total_sales = len(sales)
        total_revenue = sum(sale.total_amount for sale in sales)
        total_profit = sum(sale.profit for sale in sales)
        
        return {
            "report_type": "Daily",
            "date": date.strftime("%Y-%m-%d"),
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "total_profit": total_profit,
            "profit_margin": (total_profit / total_revenue * 100) if total_revenue > 0 else 0,
        }
    
    @staticmethod
    def get_weekly_report(db: Session, date: datetime) -> Dict[str, Any]:
        """Get weekly report"""
        start = date - timedelta(days=date.weekday())
        end = start + timedelta(days=6)
        
        sales = db.query(Sale).filter(
            Sale.sale_date >= start,
            Sale.sale_date <= end
        ).all()
        
        total_sales = len(sales)
        total_revenue = sum(sale.total_amount for sale in sales)
        total_profit = sum(sale.profit for sale in sales)
        
        return {
            "report_type": "Weekly",
            "week_start": start.strftime("%Y-%m-%d"),
            "week_end": end.strftime("%Y-%m-%d"),
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "total_profit": total_profit,
            "profit_margin": (total_profit / total_revenue * 100) if total_revenue > 0 else 0,
        }
    
    @staticmethod
    def get_monthly_report(db: Session, year: int, month: int) -> Dict[str, Any]:
        """Get monthly report"""
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        sales = db.query(Sale).filter(
            Sale.sale_date >= start,
            Sale.sale_date <= end
        ).all()
        
        total_sales = len(sales)
        total_revenue = sum(sale.total_amount for sale in sales)
        total_profit = sum(sale.profit for sale in sales)
        
        return {
            "report_type": "Monthly",
            "month": f"{year}-{month:02d}",
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "total_profit": total_profit,
            "profit_margin": (total_profit / total_revenue * 100) if total_revenue > 0 else 0,
        }
