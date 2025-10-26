import random
from datetime import datetime, timedelta, date
from faker import Faker
import uuid
from decimal import Decimal

# Import models
from app.models.base import SessionLocal, init_db
from app.models.suppliers import Supplier
from app.models.products import Product
from app.models.sales import Sale
from app.models.inventory_ledger import InventoryLedger, TransactionReason
from app.models.purchase_orders import PurchaseOrder
from app.models.returns import Return
from app.models.promotions import Promotion
from app.models.calendar_events import CalendarEvent, EventType



fake = Faker('en_IN')  # Indian locale
Faker.seed(42)
random.seed(42)

def clear_db(db):
    """Delete all data in the right order to avoid FK constraint errors"""
    # Delete child tables first (tables that reference others)
    db.query(Return).delete()           # Returns reference Sales
    db.query(InventoryLedger).delete()
    db.query(Promotion).delete()
    db.query(CalendarEvent).delete()
    db.query(Sale).delete()             # Now safe
    db.query(PurchaseOrder).delete()
    db.query(Product).delete()
    db.query(Supplier).delete()
    
    db.commit()
    print("✓ Cleared existing data from all tables")



def create_suppliers(db):
    """Create 6 suppliers"""
    supplier_names = [
        "Varanasi Silk Traders",
        "Chennai Textiles Ltd",
        "Mumbai Fashion House",
        "Delhi Designer Wear",
        "Surat Fabric Emporium",
        "Kolkata Heritage Sarees"
    ]
    
    suppliers = []
    for name in supplier_names:
        supplier = Supplier(
            name=name,
            contact=fake.phone_number()[:15],
            email=fake.email(),
            lead_time_days=random.randint(5, 15),
            active=True
        )
        suppliers.append(supplier)
        db.add(supplier)
    
    db.commit()
    print(f"✓ Created {len(suppliers)} suppliers")
    return suppliers

def create_products(db, suppliers):
    """Create 100 realistic Indian ethnic wear products"""
    
    # Saree configurations
    saree_types = [
        ("Banarasi Silk Saree", "Saree", "Banarasi", "Silk", (5000, 15000)),
        ("Kanjivaram Silk Saree", "Saree", "Kanjivaram", "Silk", (8000, 18000)),
        ("Chanderi Saree", "Saree", "Chanderi", "Cotton Silk", (3000, 8000)),
        ("Bandhani Saree", "Saree", "Bandhani", "Georgette", (2500, 7000)),
        ("Patola Saree", "Saree", "Patola", "Silk", (10000, 25000)),
        ("Tant Saree", "Saree", "Tant", "Cotton", (2000, 5000)),
    ]
    
    # Suit configurations
    suit_types = [
        ("Anarkali Suit", "Suit", "Anarkali", "Georgette", (2500, 8000)),
        ("Patiala Suit", "Suit", "Patiala", "Cotton", (1500, 4000)),
        ("Straight Cut Suit", "Suit", "Straight Cut", "Chanderi", (2000, 6000)),
        ("Palazzo Suit", "Suit", "Palazzo", "Rayon", (1800, 5000)),
        ("Sharara Suit", "Suit", "Sharara", "Silk", (3500, 9000)),
    ]
    
    colors = ["Red", "Blue", "Green", "Pink", "Yellow", "Orange", "Purple", "Maroon", 
              "Teal", "Magenta", "Golden", "Silver", "Cream", "Peach", "Turquoise"]
    
    sizes = ["Free Size", "S", "M", "L", "XL", "XXL"]
    seasons = ["Festive", "Wedding", "Casual", "Party", "Traditional", "Summer", "Winter"]
    brands = ["Saree House", "Ethnic Vista", "Royal Collection", "Designer's Choice", 
              "Traditional Elegance", "Fashion Fiesta"]
    
    products = []
    product_counter = 1
    
    # Create 60 sarees
    for _ in range(60):
        saree_type = random.choice(saree_types)
        price_range = saree_type[4]
        sell_price = random.randint(price_range[0], price_range[1])
        cost_price = int(sell_price * random.uniform(0.55, 0.70))
        
        product = Product(
            sku=f"SAR-{product_counter:04d}",
            name=f"{random.choice(colors)} {saree_type[0]}",
            category=saree_type[1],
            subcategory=saree_type[2],
            brand=random.choice(brands),
            size="Free Size",
            color=random.choice(colors),
            fabric=saree_type[3],
            cost_price=Decimal(str(cost_price)),
            sell_price=Decimal(str(sell_price)),
            reorder_point=random.randint(3, 8),
            lead_time_days=random.randint(7, 14),
            supplier_id=random.choice(suppliers).supplier_id,
            season_tag=random.choice(seasons),
            hsn_code="5407",  # HSN code for silk fabrics
            active=True
        )
        products.append(product)
        db.add(product)
        product_counter += 1
    
    # Create 40 suits
    for _ in range(40):
        suit_type = random.choice(suit_types)
        price_range = suit_type[4]
        sell_price = random.randint(price_range[0], price_range[1])
        cost_price = int(sell_price * random.uniform(0.55, 0.70))
        
        product = Product(
            sku=f"SUT-{product_counter:04d}",
            name=f"{random.choice(colors)} {suit_type[0]}",
            category=suit_type[1],
            subcategory=suit_type[2],
            brand=random.choice(brands),
            size=random.choice(sizes),
            color=random.choice(colors),
            fabric=suit_type[3],
            cost_price=Decimal(str(cost_price)),
            sell_price=Decimal(str(sell_price)),
            reorder_point=random.randint(4, 10),
            lead_time_days=random.randint(7, 14),
            supplier_id=random.choice(suppliers).supplier_id,
            season_tag=random.choice(seasons),
            hsn_code="6204",  # HSN code for women's suits
            active=True
        )
        products.append(product)
        db.add(product)
        product_counter += 1
    
    db.commit()
    print(f"✓ Created {len(products)} products")
    return products

def create_calendar_events(db):
    """Create 15 calendar events for festivals and holidays"""
    events_data = [
        (date(2024, 8, 15), "Independence Day", EventType.HOLIDAY, "All India"),
        (date(2024, 8, 26), "Janmashtami", EventType.FESTIVAL, "All India"),
        (date(2024, 9, 16), "Onam", EventType.FESTIVAL, "Kerala"),
        (date(2024, 10, 2), "Gandhi Jayanti", EventType.HOLIDAY, "All India"),
        (date(2024, 10, 12), "Dussehra", EventType.FESTIVAL, "All India"),
        (date(2024, 10, 20), "Karva Chauth", EventType.FESTIVAL, "North India"),
        (date(2024, 11, 1), "Diwali", EventType.FESTIVAL, "All India"),
        (date(2024, 11, 15), "Guru Nanak Jayanti", EventType.FESTIVAL, "Punjab"),
        (date(2024, 12, 25), "Christmas", EventType.HOLIDAY, "All India"),
        (date(2025, 1, 14), "Makar Sankranti", EventType.FESTIVAL, "All India"),
        (date(2025, 1, 26), "Republic Day", EventType.HOLIDAY, "All India"),
        (date(2025, 3, 14), "Holi", EventType.FESTIVAL, "All India"),
        (date(2025, 3, 31), "Eid al-Fitr", EventType.FESTIVAL, "All India"),
        (date(2025, 4, 10), "Ram Navami", EventType.FESTIVAL, "All India"),
        (date(2025, 5, 1), "Wedding Season Sale", EventType.SALE, "All India"),
    ]
    
    events = []
    for event_date, name, event_type, region in events_data:
        event = CalendarEvent(
            date=event_date,
            name=name,
            type=event_type,
            region=region
        )
        events.append(event)
        db.add(event)
    
    db.commit()
    print(f"✓ Created {len(events)} calendar events")
    return events

def initialize_inventory(db, products):
    """Initialize inventory for all products with purchase orders"""
    start_date = date(2024, 5, 1)
    
    for product in products:
        initial_qty = random.randint(10, 30)
        
        # Create purchase order
        po = PurchaseOrder(
            supplier_id=product.supplier_id,
            sku=product.sku,
            qty_ordered=initial_qty,
            qty_received=initial_qty,
            order_date=start_date,
            expected_date=start_date + timedelta(days=product.lead_time_days),
            received_date=start_date + timedelta(days=product.lead_time_days),
            status="Received",
            unit_cost=product.cost_price
        )
        db.add(po)
        
        # Create inventory ledger entry
        ledger = InventoryLedger(
            sku=product.sku,
            timestamp=datetime.combine(start_date, datetime.min.time()),
            change_qty=initial_qty,
            balance_qty=initial_qty,
            reason=TransactionReason.PURCHASE,
            reference_id=str(po.po_id)
        )
        db.add(ledger)
    
    db.commit()
    print(f"✓ Initialized inventory for {len(products)} products")

def create_sales(db, products):
    """Create 6 months of sales data (May 2024 - October 2024)"""
    start_date = date(2024, 5, 1)
    end_date = date(2024, 10, 31)
    
    # Get current inventory balances
    inventory = {}
    for product in products:
        latest = db.query(InventoryLedger).filter_by(sku=product.sku).order_by(
            InventoryLedger.timestamp.desc()
        ).first()
        inventory[product.sku] = latest.balance_qty if latest else 0
    
    current_date = start_date
    invoice_counter = 1
    sales_created = 0
    
    payment_modes = ["Cash", "Card", "UPI", "NetBanking"]
    
    while current_date <= end_date:
        # More sales on weekends
        is_weekend = current_date.weekday() >= 5
        is_festival = current_date in [
            date(2024, 8, 26), date(2024, 10, 12), date(2024, 10, 20), date(2024, 11, 1)
        ]
        
        if is_festival:
            num_sales = random.randint(20, 35)
        elif is_weekend:
            num_sales = random.randint(15, 25)
        else:
            num_sales = random.randint(8, 18)
        
        for _ in range(num_sales):
            # Select product with available inventory
            available_products = [p for p in products if inventory.get(p.sku, 0) > 0]
            if not available_products:
                break
            
            product = random.choice(available_products)
            quantity = 1  # Usually 1 item per sale for ethnic wear
            
            # Calculate pricing
            unit_price = product.sell_price
            discount = Decimal(str(random.choice([0, 0, 0, 5, 10, 15])))
            subtotal = unit_price * quantity
            discount_amount = subtotal * (discount / 100)
            taxable = subtotal - discount_amount
            gst_amount = taxable * Decimal("0.05")  # 5% GST
            total = taxable + gst_amount
            
            sale_time = datetime.combine(
                current_date,
                datetime.min.time().replace(
                    hour=random.randint(10, 20),
                    minute=random.randint(0, 59)
                )
            )
            
            sale = Sale(
                timestamp=sale_time,
                sku=product.sku,
                quantity=quantity,
                unit_price=unit_price,
                discount=discount_amount,
                gst_amount=gst_amount,
                total=total,
                payment_mode=random.choice(payment_modes),
                invoice_number=f"INV-{current_date.strftime('%Y%m')}-{invoice_counter:04d}",
                customer_phone=fake.phone_number()[:15] if random.random() > 0.3 else None
            )
            db.add(sale)
            
            # Update inventory ledger
            inventory[product.sku] -= quantity
            ledger = InventoryLedger(
                sku=product.sku,
                timestamp=sale_time,
                change_qty=-quantity,
                balance_qty=inventory[product.sku],
                reason=TransactionReason.SALE,
                reference_id=str(sale.sale_id)
            )
            db.add(ledger)
            
            invoice_counter += 1
            sales_created += 1
            
            # Commit in batches
            if sales_created % 100 == 0:
                db.commit()
        
        current_date += timedelta(days=1)
    
    db.commit()
    print(f"✓ Created {sales_created} sales transactions")

def create_returns(db):
    """Create some return transactions"""
    # Get recent sales
    sales = db.query(Sale).order_by(Sale.timestamp.desc()).limit(50).all()
    
    return_reasons = [
        "Wrong size",
        "Color mismatch",
        "Defective product",
        "Changed mind",
        "Quality issue"
    ]
    conditions = ["New", "Good", "Damaged"]
    
    returns_created = 0
    for sale in random.sample(sales, min(10, len(sales))):
        return_obj = Return(
            sale_id=sale.sale_id,
            sku=sale.sku,
            qty=1,
            reason=random.choice(return_reasons),
            condition=random.choice(conditions),
            restock=random.choice([True, False]),
            timestamp=sale.timestamp + timedelta(days=random.randint(1, 7))
        )
        db.add(return_obj)
        
        # If restock, update inventory
        if return_obj.restock:
            latest = db.query(InventoryLedger).filter_by(sku=sale.sku).order_by(
                InventoryLedger.timestamp.desc()
            ).first()
            
            new_balance = latest.balance_qty + 1
            ledger = InventoryLedger(
                sku=sale.sku,
                timestamp=return_obj.timestamp,
                change_qty=1,
                balance_qty=new_balance,
                reason=TransactionReason.RETURN,
                reference_id=str(return_obj.return_id)
            )
            db.add(ledger)
        
        returns_created += 1
    
    db.commit()
    print(f"✓ Created {returns_created} return transactions")

def create_promotions(db):
    """Create some promotional campaigns"""
    promotions_data = [
        ("Diwali Mega Sale", date(2024, 10, 25), date(2024, 11, 5), 20),
        ("Summer Collection Sale", date(2024, 5, 15), date(2024, 6, 15), 15),
        ("Monsoon Special", date(2024, 7, 1), date(2024, 8, 31), 10),
        ("Wedding Season Discount", date(2024, 11, 15), date(2024, 12, 31), 25),
    ]
    
    for name, start, end, discount in promotions_data:
        promo = Promotion(
            name=name,
            start_date=start,
            end_date=end,
            discount_pct=Decimal(str(discount)),
            active=True
        )
        db.add(promo)
    
    db.commit()
    print(f"✓ Created {len(promotions_data)} promotions")

def main():
    """Main seeding function"""
    print("=" * 60)
    print("Starting database seeding...")
    print("=" * 60)

    # Initialize database
    init_db()

    # Create session
    db = SessionLocal()  # <-- Make sure this line comes BEFORE using db

    try:
        clear_db(db)  # <-- Now db exists, safe to call
        suppliers = create_suppliers(db)
        products = create_products(db, suppliers)
        events = create_calendar_events(db)
        initialize_inventory(db, products)
        create_sales(db, products)
        create_returns(db)
        create_promotions(db)

        print("=" * 60)
        print("✓ Database seeding completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"✗ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()