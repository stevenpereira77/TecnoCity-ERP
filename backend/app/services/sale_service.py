"""
Sale service - Business logic for sales management
"""
from sqlalchemy.orm import Session
from app.models.sale import Sale, SaleItem, SaleStatus
from app.models.product import Product
from app.models.customer import Customer
from app.models.inventory_movement import InventoryMovement, MovementType
from app.schemas.sale import SaleCreate
from typing import List, Optional
from datetime import datetime

class SaleService:
    
    @staticmethod
    def create_sale(db: Session, sale: SaleCreate) -> Sale:
        """Create a new sale with items"""
        # Calculate totals
        subtotal = 0
        cost_of_goods = 0
        
        sale_items_data = []
        for item in sale.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise ValueError(f"Product {item.product_id} not found")
            
            item_total = item.unit_price * item.quantity
            item_cost = item.cost_price * item.quantity
            item_profit = item_total - item_cost
            
            subtotal += item_total
            cost_of_goods += item_cost
            
            sale_items_data.append({
                'product_id': item.product_id,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'cost_price': item.cost_price,
                'total_price': item_total,
                'item_profit': item_profit,
            })
        
        # Create sale
        db_sale = Sale(
            sale_number=SaleService.generate_sale_number(db),
            customer_id=sale.customer_id,
            subtotal=subtotal,
            tax_amount=0,
            total_amount=subtotal,
            cost_of_goods=cost_of_goods,
            profit=subtotal - cost_of_goods,
            payment_method=sale.payment_method,
            notes=sale.notes,
        )
        
        db.add(db_sale)
        db.flush()
        
        # Create sale items and update inventory
        for item_data in sale_items_data:
            sale_item = SaleItem(**item_data, sale_id=db_sale.id)
            db.add(sale_item)
            
            # Update product inventory
            product = db.query(Product).filter(Product.id == item_data['product_id']).first()
            quantity_before = product.quantity_available
            product.quantity_available -= item_data['quantity']
            quantity_after = product.quantity_available
            
            # Record inventory movement
            movement = InventoryMovement(
                product_id=item_data['product_id'],
                movement_type=MovementType.SALE,
                quantity_changed=-item_data['quantity'],
                quantity_before=quantity_before,
                quantity_after=quantity_after,
                reference_id=db_sale.id,
                reference_type='sale',
            )
            db.add(movement)
        
        # Update customer if exists
        if sale.customer_id:
            customer = db.query(Customer).filter(Customer.id == sale.customer_id).first()
            if customer:
                customer.total_spent += subtotal
                customer.total_purchases += 1
        
        db.commit()
        db.refresh(db_sale)
        return db_sale
    
    @staticmethod
    def get_sale(db: Session, sale_id: int) -> Optional[Sale]:
        """Get sale by ID"""
        return db.query(Sale).filter(Sale.id == sale_id).first()
    
    @staticmethod
    def get_all_sales(db: Session, skip: int = 0, limit: int = 100) -> List[Sale]:
        """Get all sales with pagination"""
        return db.query(Sale).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_sales_by_date(db: Session, start_date: datetime, end_date: datetime) -> List[Sale]:
        """Get sales between dates"""
        return db.query(Sale).filter(
            Sale.sale_date >= start_date,
            Sale.sale_date <= end_date
        ).all()
    
    @staticmethod
    def get_daily_sales(db: Session, date: datetime) -> List[Sale]:
        """Get sales for a specific day"""
        start = datetime(date.year, date.month, date.day, 0, 0, 0)
        end = datetime(date.year, date.month, date.day, 23, 59, 59)
        return SaleService.get_sales_by_date(db, start, end)
    
    @staticmethod
    def generate_sale_number(db: Session) -> str:
        """Generate unique sale number"""
        last_sale = db.query(Sale).order_by(Sale.id.desc()).first()
        if not last_sale:
            return "SALE-000001"
        sale_id = int(last_sale.sale_number.split('-')[1]) + 1
        return f"SALE-{sale_id:06d}"
    
    @staticmethod
    def calculate_daily_sales(db: Session, date: datetime) -> float:
        """Calculate total sales for a day"""
        sales = SaleService.get_daily_sales(db, date)
        return sum(sale.total_amount for sale in sales)
    
    @staticmethod
    def calculate_monthly_sales(db: Session, year: int, month: int) -> float:
        """Calculate total sales for a month"""
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1)
        else:
            end = datetime(year, month + 1, 1)
        sales = SaleService.get_sales_by_date(db, start, end)
        return sum(sale.total_amount for sale in sales)
    
    @staticmethod
    def calculate_daily_profit(db: Session, date: datetime) -> float:
        """Calculate total profit for a day"""
        sales = SaleService.get_daily_sales(db, date)
        return sum(sale.profit for sale in sales)
