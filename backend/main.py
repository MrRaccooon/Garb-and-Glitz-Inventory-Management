"""
FastAPI application initialization for Garb & Glitz Inventory Management System.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from sqlalchemy import text

from app.config import settings
from app.dependencies import get_db
from app.api.v1 import products, sales, inventory, forecasting, analytics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events for the application.
    """
    # Startup
    logger.info("API starting up...")
    
    # Verify database connection
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        logger.info("Database connection verified successfully")
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise
    finally:
        db.close()
    
    yield
    
    # Shutdown
    logger.info("API shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="Garb & Glitz Inventory API",
    version="1.0",
    description="Comprehensive inventory management system with analytics and forecasting",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(products.router, prefix="/api/v1", tags=["Products"])
app.include_router(sales.router, prefix="/api/v1", tags=["Sales"])
app.include_router(inventory.router, prefix="/api/v1", tags=["Inventory"])
app.include_router(forecasting.router, prefix="/api/v1", tags=["Forecasting"])
app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """
    Health check endpoint to verify API is running.
    
    Returns:
        dict: Status and environment information
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "1.0"
    }


@app.get("/", tags=["Root"])
async def root() -> dict:
    """
    Root endpoint with API information.
    
    Returns:
        dict: Welcome message and documentation link
    """
    return {
        "message": "Welcome to Garb & Glitz Inventory API",
        "docs": "/docs",
        "health": "/health"
    }