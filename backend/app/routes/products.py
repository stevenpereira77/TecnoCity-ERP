"""
Product routes - API endpoints for product management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.product_service import ProductService
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from typing import List

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    try:
        db_product = ProductService.create_product(db, product)
        return db_product
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[ProductResponse])
def get_products(skip: int = Query(0), limit: int = Query(100), db: Session = Depends(get_db)):
    """Get all products"""
    return ProductService.get_all_products(db, skip, limit)

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get product by ID"""
    product = ProductService.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/code/{code}", response_model=ProductResponse)
def get_product_by_code(code: str, db: Session = Depends(get_db)):
    """Get product by code"""
    product = ProductService.get_product_by_code(db, code)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/category/{category}", response_model=List[ProductResponse])
def get_products_by_category(category: str, db: Session = Depends(get_db)):
    """Get products by category"""
    return ProductService.get_products_by_category(db, category)

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    """Update a product"""
    db_product = ProductService.update_product(db, product_id, product)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product"""
    success = ProductService.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

@router.get("/search/{query}", response_model=List[ProductResponse])
def search_products(query: str, db: Session = Depends(get_db)):
    """Search products"""
    return ProductService.search_products(db, query)

@router.get("/low-stock/list", response_model=List[ProductResponse])
def get_low_stock_products(db: Session = Depends(get_db)):
    """Get low stock products"""
    return ProductService.get_low_stock_products(db)

@router.get("/out-of-stock/list", response_model=List[ProductResponse])
def get_out_of_stock_products(db: Session = Depends(get_db)):
    """Get out of stock products"""
    return ProductService.get_out_of_stock_products(db)
