"""
FastAPI dependencies for database sessions and error handling.
"""
from typing import Generator, Callable
from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
import logging

from app.config import settings

logger = logging.getLogger(__name__)


# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.ENVIRONMENT == "development"
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency that yields a SQLAlchemy session.
    
    Yields:
        Session: SQLAlchemy database session
        
    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    finally:
        db.close()


def handle_db_errors(func: Callable) -> Callable:
    """
    Decorator to handle database errors in route handlers.
    
    Args:
        func: The route handler function to wrap
        
    Returns:
        Callable: Wrapped function with error handling
        
    Example:
        @router.get("/items")
        @handle_db_errors
        async def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except SQLAlchemyError as e:
            logger.error(f"Database error in {func._name_}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while processing your request"
            )
        except ValueError as e:
            logger.warning(f"Validation error in {func._name_}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error in {func._name_}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred"
            )
    
    return wrapper


def validate_pagination(skip: int = 0, limit: int = 50) -> tuple[int, int]:
    """
    Validate and normalize pagination parameters.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        tuple[int, int]: Validated (skip, limit) values

    Raises:
        HTTPException: If parameters are invalid
    """
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skip parameter must be non-negative"
        )

    if limit < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit parameter must be positive"
        )

    if limit > settings.MAX_PAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Limit cannot exceed {settings.MAX_PAGE_SIZE}"
        )

    return skip, limit


def init_db():
    """
    Initialize the database by creating all tables.
    """
    try:
        from app.models.base import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error initializing database: {e}")
        raise


def drop_db():
    """
    Drop all database tables.
    WARNING: This will delete all data!
    """
    try:
        from app.models.base import Base
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error dropping database: {e}")
        raise