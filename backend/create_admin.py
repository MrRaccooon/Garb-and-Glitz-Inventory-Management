"""
Simple script to create admin user with fixed bcrypt handling
"""
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.dependencies import SessionLocal
from app.models.users import User
import bcrypt

def create_admin_user():
    """Create admin user using bcrypt directly"""
    print("\n👤 Creating admin user...")

    session = SessionLocal()

    try:
        # Check if admin already exists
        existing_admin = session.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("✓ Admin user already exists")
            print("    Username: admin")
            print("    Password: admin123")
            return True

        # Hash password using bcrypt directly (avoiding passlib compatibility issue)
        password = b"admin123"
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password, salt).decode('utf-8')

        # Create admin user
        admin = User(
            username="admin",
            email="admin@garbandglitz.com",
            full_name="System Administrator",
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=True
        )
        session.add(admin)
        session.commit()

        print("✓ Admin user created successfully")
        print("    Username: admin")
        print("    Password: admin123")
        print("    ⚠️  Change password after first login!")
        return True

    except Exception as e:
        session.rollback()
        print(f"✗ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    print("=" * 70)
    print("🔐 Creating Admin User")
    print("=" * 70)

    success = create_admin_user()

    if success:
        print("\n✅ Admin user setup complete!")
        print("\n🚀 Next steps:")
        print("  1. Start the API: uvicorn app.main:app --reload")
        print("  2. Login with username: admin, password: admin123")
    else:
        print("\n❌ Admin user creation failed")
        sys.exit(1)
