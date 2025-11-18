"""
Base model for SQLAlchemy ORM models.
This module only contains the declarative base - engine and session are in dependencies.py
"""
from sqlalchemy.orm import declarative_base

# Declarative base for all models
Base = declarative_base()
