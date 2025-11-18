"""
Complete Database Setup Script with Sample Data
Creates all tables, admin user, and populates with 6 months of sample data
"""
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.dependencies import engine, SessionLocal
from app.models.base import Base
from app.models.users import User
from app.models.products import Product
from app.models.suppliers import Supplier
from app.models.sales import Sale
from app.models.inventory_ledger import InventoryLedger, TransactionReason
from app.auth import get_password_hash
from faker import Faker
import uuid

fake = Faker()


def drop_all_tables():
    """Drop all existing tables"""
    print("\n🗑️  Dropping existing tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        print("✓ All tables dropped")
        return True
    except Exception as e:
        print(f"✗ Error dropping tables: {e}")
        return False


def create_all_tables():
    """Create all database tables"""
    print("\n📦 Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ All tables created successfully")

        # List all created tables
        print("\n  Created tables:")
        for table in Base.metadata.sorted_tables:
            print(f"    - {table.name}")

        return True
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False


def create_admin_user(session):
    """Create admin user"""
    print("\n👤 Creating admin user...")
    try:
        # Use shorter password to avoid bcrypt 72-byte limit
        admin = User(
            username="admin",
            email="admin@garbandglitz.com",
            full_name="System Administrator",
            hashed_password=get_password_hash("admin123"),  # Short password, safe for bcrypt
            is_active=True,
            is_superuser=True
        )
        session.add(admin)
        session.commit()

        print("✓ Admin user created")
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


def create_suppliers(session):
    """Create sample suppliers"""
    print("\n🏭 Creating suppliers...")

    suppliers_data = [
        {
            "name": "Mumbai Silk House",
            "contact": "+919876543210",
            "email": "contact@mumbaisilk.com",
            "lead_time_days": 7
        },
        {
            "name": "Delhi Fashion Textiles",
            "contact": "+919876543211",
            "email": "sales@delhifashion.com",
            "lead_time_days": 10
        },
        {
            "name": "Banarasi Saree Emporium",
            "contact": "+919876543212",
            "email": "info@banarasise.com",
            "lead_time_days": 14
        },
        {
            "name": "Kanjivaram Silk Traders",
            "contact": "+919876543213",
            "email": "orders@kanjivaramsilk.com",
            "lead_time_days": 12
        }
    ]

    suppliers = []
    for data in suppliers_data:
        supplier = Supplier(**data)
        session.add(supplier)
        suppliers.append(supplier)

    session.commit()
    print(f"✓ Created {len(suppliers)} suppliers")
    return suppliers


def create_products(session, suppliers):
    """Create sample products"""
    print("\n👗 Creating products...")

    categories = {
        "Saree": ["Banarasi", "Kanjivaram", "Silk", "Cotton", "Georgette"],
        "Suit": ["Anarkali", "Straight", "Palazzo", "A-Line"],
        "Lehenga": ["Bridal", "Party Wear", "Festive"],
        "Dupatta": ["Net", "Silk", "Georgette", "Chiffon"]
    }

    colors = ["Red", "Blue", "Green", "Yellow", "Pink", "Black", "White", "Multi", "Golden", "Silver"]
    fabrics = ["Silk", "Cotton", "Georgette", "Chiffon", "Net", "Velvet", "Crepe"]
    sizes = ["Free Size", "S", "M", "L", "XL", "XXL"]

    products = []
    sku_counter = {"Saree": 1, "Suit": 1, "Lehenga": 1, "Dupatta": 1}

    for category, subcategories in categories.items():
        # Create 20 products per category
        for _ in range(20):
            prefix = category[:3].upper()
            sku = f"{prefix}{sku_counter[category]:03d}"
            sku_counter[category] += 1

            cost_price = Decimal(random.randint(500, 5000))
            sell_price = cost_price * Decimal(random.uniform(1.3, 2.5))

            product = Product(
                sku=sku,
                name=f"{random.choice(subcategories)} {category}",
                category=category,
                subcategory=random.choice(subcategories),
                brand=random.choice(["House Brand", "Premium Collection", "Designer Line"]),
                size=random.choice(sizes),
                color=random.choice(colors),
                fabric=random.choice(fabrics),
                cost_price=cost_price,
                sell_price=sell_price,
                reorder_point=random.randint(5, 20),
                lead_time_days=random.randint(5, 14),
                supplier_id=random.choice(suppliers).supplier_id if random.random() > 0.3 else None,
                season_tag=random.choice(["Summer", "Winter", "Festive", "Wedding", "Casual"]),
                active=True
            )
            session.add(product)
            products.append(product)

    session.commit()
    print(f"✓ Created {len(products)} products")
    return products


def create_inventory_and_sales(session, products):
    """Create inventory entries and sales for past 6 months"""
    print("\n📊 Creating inventory and sales data (6 months)...")

    # Start date: 6 months ago
    start_date = datetime.utcnow() - timedelta(days=180)

    # Initial inventory
    print("  📦 Adding initial inventory...")
    for product in products:
        initial_qty = random.randint(10, 100)
        ledger = InventoryLedger(
            sku=product.sku,
            change_qty=initial_qty,
            balance_qty=initial_qty,
            reason=TransactionReason.PURCHASE,
            timestamp=start_date
        )
        session.add(ledger)

    session.commit()

    # Create sales over 6 months
    print("  💰 Generating 6 months of sales...")

    payment_modes = ["Cash", "Card", "UPI", "NetBanking"]
    total_sales = 0

    for day in range(180):
        current_date = start_date + timedelta(days=day)

        # Random number of sales per day (2-10)
        num_sales = random.randint(2, 10)

        for _ in range(num_sales):
            product = random.choice(products)

            # Get current stock
            current_stock = session.query(InventoryLedger).filter(
                InventoryLedger.sku == product.sku
            ).order_by(InventoryLedger.timestamp.desc()).first()

            if current_stock and current_stock.balance_qty > 0:
                # Random quantity (1-3 items)
                quantity = min(random.randint(1, 3), current_stock.balance_qty)

                # Calculate prices
                unit_price = product.sell_price
                discount = unit_price * Decimal(random.uniform(0, 0.1))  # 0-10% discount
                subtotal = (unit_price - discount) * quantity
                gst_amount = subtotal * Decimal(0.12)  # 12% GST
                total = subtotal + gst_amount

                # Create sale
                sale = Sale(
                    timestamp=current_date + timedelta(hours=random.randint(9, 20)),
                    sku=product.sku,
                    quantity=quantity,
                    unit_price=unit_price,
                    discount=discount * quantity,
                    gst_amount=gst_amount,
                    total=total,
                    payment_mode=random.choice(payment_modes),
                    invoice_number=f"INV-{current_date.strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}",
                    customer_phone=f"+91{random.randint(7000000000, 9999999999)}" if random.random() > 0.3 else None
                )
                session.add(sale)

                # Update inventory
                new_balance = current_stock.balance_qty - quantity
                ledger = InventoryLedger(
                    sku=product.sku,
                    change_qty=-quantity,
                    balance_qty=new_balance,
                    reason=TransactionReason.SALE,
                    timestamp=sale.timestamp
                )
                session.add(ledger)

                total_sales += 1

        # Commit every 10 days to avoid huge transactions
        if day % 10 == 0:
            session.commit()
            print(f"    ✓ Day {day}/180 ({total_sales} sales so far)")

    session.commit()
    print(f"✓ Created {total_sales} sales transactions over 6 months")


def main():
    """Main setup function"""
    print("=" * 70)
    print("🏪 Garb & Glitz Inventory - Complete Database Setup")
    print("=" * 70)

    # Ask for confirmation
    print("\n⚠️  WARNING: This will:")
    print("  1. DROP all existing tables and data")
    print("  2. CREATE fresh tables")
    print("  3. POPULATE with sample data (6 months)")
    print("\n✓ Proceeding with setup...")

    # Auto-confirm for non-interactive runs
    # response = input("\nDo you want to continue? (yes/no): ")
    # if response.lower() not in ['yes', 'y']:
    #     print("\n❌ Setup cancelled")
    #     return

    # Drop existing tables
    if not drop_all_tables():
        print("\n❌ Setup failed at drop tables step")
        return

    # Create tables
    if not create_all_tables():
        print("\n❌ Setup failed at create tables step")
        return

    # Create session
    session = SessionLocal()

    try:
        # Create admin user
        if not create_admin_user(session):
            print("\n⚠️  Warning: Admin user creation failed")

        # Create suppliers
        suppliers = create_suppliers(session)
        if not suppliers:
            print("\n❌ Setup failed at suppliers step")
            return

        # Create products
        products = create_products(session, suppliers)
        if not products:
            print("\n❌ Setup failed at products step")
            return

        # Create inventory and sales
        create_inventory_and_sales(session, products)

        print("\n" + "=" * 70)
        print("✅ Database setup complete!")
        print("=" * 70)

        print("\n📊 Summary:")
        print(f"  - Users: 1 (admin)")
        print(f"  - Suppliers: {len(suppliers)}")
        print(f"  - Products: {len(products)}")
        print(f"  - Time period: Last 6 months")
        print(f"  - Inventory ledger entries: Created")
        print(f"  - Sales transactions: Generated")

        print("\n🚀 Next steps:")
        print("  1. Start the API: uvicorn app.main:app --reload")
        print("  2. Login with username: admin, password: admin123")
        print("  3. Explore Analytics, Forecasting, and other pages")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    main()
