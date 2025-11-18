# Quick Start Guide - Database Setup

## Prerequisites
Make sure PostgreSQL is installed and running with these credentials:
- Database: `inventory_db`
- User: `inventory`
- Password: `password`
- Host: `localhost`
- Port: `5432`

## Step 1: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

If you encounter any errors, install core packages individually:

```bash
# Core packages
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic pydantic-settings

# Authentication
pip install python-jose[cryptography] passlib[bcrypt] email-validator

# Data processing
pip install pandas numpy

# Utilities
pip install python-dotenv faker python-multipart
```

## Step 2: Initialize Database with Sample Data

Run the comprehensive setup script that will:
- Create all tables (users, products, suppliers, sales, inventory, etc.)
- Create admin user (username: admin, password: admin123)
- Populate with 4 suppliers
- Create 80 products across all categories
- Generate 6 months of sales data
- Create inventory ledger entries

```bash
cd backend
python setup_database.py
```

When prompted, type `yes` to confirm.

## Step 3: Start the Backend API

```bash
cd backend
uvicorn app.main:app --reload
```

The API will be available at:
- Main API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Step 4: Start the Frontend

```bash
cd frontend
npm install  # If not done already
npm run dev
```

## Step 5: Login

Use these credentials:
- Username: `admin`
- Password: `admin123`

**⚠️ IMPORTANT: Change the admin password after first login!**

## What Gets Created

### Database Tables
- `users` - Authentication and user management
- `products` - Product catalog (80 items)
- `suppliers` - Supplier information (4 suppliers)
- `sales` - Sales transactions (6 months of data)
- `inventory_ledger` - Inventory tracking
- `purchase_orders` - Purchase order management
- `returns` - Return transactions
- `promotions` - Promotional campaigns
- `calendar_events` - Event scheduling

### Sample Data
- **Products**: 80 items across 4 categories
  - 20 Sarees (Banarasi, Kanjivaram, etc.)
  - 20 Suits (Anarkali, Straight, Palazzo, A-Line)
  - 20 Lehengas (Bridal, Party Wear, Festive)
  - 20 Dupattas (Net, Silk, Georgette, Chiffon)

- **Suppliers**: 4 suppliers
  - Mumbai Silk House
  - Delhi Fashion Textiles
  - Banarasi Saree Emporium
  - Kanjivaram Silk Traders

- **Sales**: ~1,000+ transactions over 6 months
- **Inventory**: Tracked in ledger with initial stock

## Testing the Application

### 1. Test Authentication
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 2. Test Products API
```bash
curl http://localhost:8000/api/v1/products
```

### 3. Test Analytics
```bash
curl http://localhost:8000/api/v1/summary?days=30
```

### 4. Test Forecasting
```bash
curl "http://localhost:8000/api/v1/forecast?sku=SAR001&horizon=4w"
```

## Features Now Available

✅ **Products Management**
- Add, edit, delete products
- Search and filter
- Supplier linking

✅ **Sales Tracking**
- Record sales
- View sales history
- Bulk import from CSV

✅ **Inventory Management**
- Real-time stock tracking
- Low stock alerts
- Inventory ledger

✅ **Analytics Dashboard**
- Revenue metrics
- Top products
- Category breakdown
- Custom time periods

✅ **Demand Forecasting**
- AI-based predictions
- Confidence intervals
- Recommended reorder quantities

✅ **Authentication**
- Secure JWT-based login
- User management
- Role-based access (admin/user)

## Troubleshooting

### Database Connection Error
Make sure PostgreSQL is running and the database exists:
```sql
CREATE DATABASE inventory_db;
CREATE USER inventory WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE inventory_db TO inventory;
```

### Import Errors
Install missing packages:
```bash
pip install <package-name>
```

### Port Already in Use
If port 8000 is busy, specify a different port:
```bash
uvicorn app.main:app --reload --port 8001
```

## Next Steps

1. ✅ Login to the application
2. ✅ Explore the Analytics page to see 6 months of data
3. ✅ Test the Forecasting page with any product SKU
4. ✅ Try adding/editing products
5. ✅ Record new sales
6. ✅ Change the admin password!

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

All API endpoints are documented there with examples and schemas.
