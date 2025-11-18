"""
Database initialization script
Creates all tables and optionally creates an admin user
"""
import sys
from app.dependencies import engine, init_db
from app.models.base import Base
from app.models import User
from app.auth import get_password_hash
from sqlalchemy.orm import Session


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Tables created successfully")
        return True
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False


def create_admin_user():
    """Create an admin user if it doesn't exist"""
    print("\nCreating admin user...")

    session = Session(bind=engine)
    try:
        # Check if admin already exists
        existing_admin = session.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("✓ Admin user already exists")
            return True

        # Create admin user
        admin = User(
            username="admin",
            email="admin@garbandglitz.com",
            full_name="System Administrator",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True
        )

        session.add(admin)
        session.commit()
        print("✓ Admin user created successfully")
        print("\n  Username: admin")
        print("  Password: admin123")
        print("  ⚠️  Please change the password after first login!")
        return True

    except Exception as e:
        session.rollback()
        print(f"✗ Error creating admin user: {e}")
        return False
    finally:
        session.close()


def main():
    """Main initialization function"""
    print("=" * 60)
    print("Garb & Glitz Inventory Database Initialization")
    print("=" * 60)

    # Create tables
    if not create_tables():
        print("\n❌ Database initialization failed")
        sys.exit(1)

    # Create admin user
    if not create_admin_user():
        print("\n⚠️  Warning: Admin user creation failed")
        print("You can create users manually using the API")

    print("\n" + "=" * 60)
    print("✅ Database initialization complete!")
    print("=" * 60)
    print("\nYou can now start the API server with:")
    print("  uvicorn app.main:app --reload")
    print("\nAPI will be available at: http://localhost:8000")
    print("API docs: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
