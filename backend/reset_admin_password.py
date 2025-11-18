"""
Reset admin user password with bcrypt-safe truncation
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.dependencies import SessionLocal
from app.models.users import User
from app.auth import get_password_hash


def reset_admin_password():
    """Reset admin password to 'admin123' with proper bcrypt truncation"""
    print("Resetting admin password...")

    session = SessionLocal()

    try:
        # Find admin user
        admin = session.query(User).filter(User.username == "admin").first()

        if not admin:
            print("ERROR: Admin user not found!")
            return False

        # Reset password with truncation-safe hash
        new_password = "admin123"
        admin.hashed_password = get_password_hash(new_password)

        session.commit()

        print("SUCCESS: Admin password reset successfully!")
        print(f"   Username: admin")
        print(f"   Password: {new_password}")

        return True

    except Exception as e:
        session.rollback()
        print(f"ERROR: Error resetting password: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        session.close()


if __name__ == "__main__":
    reset_admin_password()
