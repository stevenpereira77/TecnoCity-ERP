"""
TecnoCity ERP - Main Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.config import APP_NAME, APP_VERSION, API_PREFIX, API_VERSION
from app.routes import products, sales, purchases, dashboard, reports

# Create FastAPI app
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Professional ERP system for tech store management"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Include routes
app.include_router(products.router, prefix=f"{API_PREFIX}/{API_VERSION}")
app.include_router(sales.router, prefix=f"{API_PREFIX}/{API_VERSION}")
app.include_router(purchases.router, prefix=f"{API_PREFIX}/{API_VERSION}")
app.include_router(dashboard.router, prefix=f"{API_PREFIX}/{API_VERSION}")
app.include_router(reports.router, prefix=f"{API_PREFIX}/{API_VERSION}")

@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
        "api_prefix": f"{API_PREFIX}/{API_VERSION}"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
