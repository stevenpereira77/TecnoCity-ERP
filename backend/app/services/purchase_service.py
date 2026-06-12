"""
Purchase service - Business logic for purchase management
"""
from sqlalchemy.orm import Session
from app.models.purchase import Purchase, PurchaseItem, PurchaseStatus
from app.models.product import Product
from app.models.inventory_movement import InventoryMovement, MovementType
from app.schemas.purchase import PurchaseCreate
from typing import List, Optional
from datetime import datetime

class PurchaseService:
    
    @staticmethod
    def create_purchase(db: Session, purchase: PurchaseCreate) -> Purchase:
        """Create a new purchase with items"""
        # Calculate total
        total_amount = 0
        purchase_items_data = []
        
        for item in purchase.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise ValueError(f"Product {item.product_id} not found")
            
            item_total = item.unit_price * item.quantity
            total_amount += item_total
            
            purchase_items_data.append({
                'product_id': item.product_id,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'total_price': item_total,
            })
        
        # Create purchase
        db_purchase = Purchase(
            purchase_number=PurchaseService.generate_purchase_number(db),
            supplier_id=purchase.supplier_id,
            total_amount=total_amount,
            expected_delivery=purchase.expected_delivery,
            notes=purchase.notes,
        )
        
        db.add(db_purchase)
        db.flush()
        
        # Create purchase items and update inventory
        for item_data in purchase_items_data:
            purchase_item = PurchaseItem(**item_data, purchase_id=db_purchase.id)
            db.add(purchase_item)
            
            # Update product inventory
            product = db.query(Product).filter(Product.id == item_data['product_id']).first()
            quantity_before = product.quantity_available
            product.quantity_available += item_data['quantity']
            quantity_after = product.quantity_available
            
            # Also update purchase price
            if product.purchase_price == 0 or product.purchase_price != item_data['unit_price']:
                product.purchase_price = item_data['unit_price']
            
            # Record inventory movement
            movement = InventoryMovement(
                product_id=item_data['product_id'],
                movement_type=MovementType.PURCHASE,
                quantity_changed=item_data['quantity'],
                quantity_before=quantity_before,
                quantity_after=quantity_after,
                reference_id=db_purchase.id,
                reference_type='purchase',
            )
            db.add(movement)
        
        db.commit()
        db.refresh(db_purchase)
        return db_purchase
    
    @staticmethod
    def get_purchase(db: Session, purchase_id: int) -> Optional[Purchase]:
        """Get purchase by ID"""
        return db.query(Purchase).filter(Purchase.id == purchase_id).first()
    
    @staticmethod
    def get_all_purchases(db: Session, skip: int = 0, limit: int = 100) -> List[Purchase]:
        """Get all purchases with pagination"""
        return db.query(Purchase).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_purchases_by_date(db: Session, start_date: datetime, end_date: datetime) -> List[Purchase]:
        """Get purchases between dates"""
        return db.query(Purchase).filter(
            Purchase.purchase_date >= start_date,
            Purchase.purchase_date <= end_date
        ).all()
    
    @staticmethod
    def mark_received(db: Session, purchase_id: int) -> Optional[Purchase]:
        """Mark purchase as received"""
        db_purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
        if db_purchase:
            db_purchase.status = PurchaseStatus.RECEIVED
            db_purchase.received_date = datetime.utcnow()
            db.commit()
            db.refresh(db_purchase)
        return db_purchase
    
    @staticmethod
    def generate_purchase_number(db: Session) -> str:
        """Generate unique purchase number"""
        last_purchase = db.query(Purchase).order_by(Purchase.id.desc()).first()
        if not last_purchase:
            return "PO-000001"
        po_id = int(last_purchase.purchase_number.split('-')[1]) + 1
        return f"PO-{po_id:06d}"
    
    @staticmethod
    def calculate_total_purchases(db: Session, start_date: datetime, end_date: datetime) -> float:
        """Calculate total purchases cost"""
        purchases = PurchaseService.get_purchases_by_date(db, start_date, end_date)
        return sum(purchase.total_amount for purchase in purchases)
