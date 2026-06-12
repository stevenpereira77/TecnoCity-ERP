"""
Product service - Business logic for product management
"""
from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from typing import List, Optional

class ProductService:
    
    @staticmethod
    def create_product(db: Session, product: ProductCreate) -> Product:
        """Create a new product"""
        db_product = Product(**product.model_dump())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    
    @staticmethod
    def get_product(db: Session, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        return db.query(Product).filter(Product.id == product_id).first()
    
    @staticmethod
    def get_product_by_code(db: Session, code: str) -> Optional[Product]:
        """Get product by code"""
        return db.query(Product).filter(Product.code == code).first()
    
    @staticmethod
    def get_all_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get all products with pagination"""
        return db.query(Product).filter(Product.is_active == True).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_products_by_category(db: Session, category: str) -> List[Product]:
        """Get products by category"""
        return db.query(Product).filter(
            Product.category == category,
            Product.is_active == True
        ).all()
    
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
    def update_product(db: Session, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
        """Update a product"""
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if db_product:
            update_data = product_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_product, field, value)
            db.commit()
            db.refresh(db_product)
        return db_product
    
    @staticmethod
    def update_stock(db: Session, product_id: int, quantity_change: int) -> Optional[Product]:
        """Update product stock"""
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if db_product:
            db_product.quantity_available += quantity_change
            db.commit()
            db.refresh(db_product)
        return db_product
    
    @staticmethod
    def delete_product(db: Session, product_id: int) -> bool:
        """Soft delete a product"""
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if db_product:
            db_product.is_active = False
            db.commit()
            return True
        return False
    
    @staticmethod
    def search_products(db: Session, query: str) -> List[Product]:
        """Search products by name or code"""
        return db.query(Product).filter(
            (Product.name.ilike(f"%{query}%") | Product.code.ilike(f"%{query}%")),
            Product.is_active == True
        ).all()
