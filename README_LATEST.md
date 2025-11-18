# Garb & Glitz Inventory Management System

**Version:** 1.0.0
**Last Updated:** November 2025

A comprehensive full-stack inventory management system designed specifically for fashion/clothing retail businesses. Built with FastAPI (Python) backend, React frontend, PostgreSQL database, and Redis caching.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Features](#2-features)
3. [Technology Stack](#3-technology-stack)
4. [System Requirements](#4-system-requirements)
5. [Installation & Setup](#5-installation--setup)
6. [Running the Application](#6-running-the-application)
7. [Project Structure](#7-project-structure)
8. [Environment Configuration](#8-environment-configuration)
9. [Database Setup](#9-database-setup)
10. [API Documentation](#10-api-documentation)
11. [Frontend Pages](#11-frontend-pages)
12. [Authentication](#12-authentication)
13. [Deployment](#13-deployment)
14. [Troubleshooting](#14-troubleshooting)
15. [Contributing](#15-contributing)
16. [License](#16-license)

---

## 1. Project Overview

**Garb & Glitz** is an enterprise-grade inventory management system designed to handle:

- **Product Management**: SKU-based tracking with categories (Sarees, Suits, Lehengas, Dupattas)
- **Real-time Inventory**: Ledger-based inventory tracking with automatic updates
- **Sales Processing**: Multi-payment mode sales with GST calculation and invoice generation
- **Demand Forecasting**: Exponential smoothing algorithm for predicting future demand
- **Analytics & Reporting**: Revenue trends, top products, ABC analysis, category breakdowns
- **Supplier Management**: Track suppliers and purchase orders
- **Low Stock Alerts**: Automated reorder point notifications
- **User Authentication**: JWT-based secure login with role-based access

### Key Capabilities

- Handle 1000+ SKUs efficiently
- Process bulk sales via CSV upload
- Generate 4-12 week demand forecasts
- Track complete audit trail via inventory ledger
- Multi-user support with role-based permissions
- Real-time stock level monitoring
- Advanced analytics with customizable time periods

---

## 2. Features

### Product Management
- ✅ Create, Read, Update, Delete (CRUD) products
- ✅ SKU-based identification (Format: ABC123)
- ✅ Categories: Saree, Suit, Lehenga, Dupatta
- ✅ Attributes: Size, Color, Fabric, Brand, Season Tag, HSN Code
- ✅ Pricing: Cost price and Sell price tracking
- ✅ Supplier linking
- ✅ Reorder point and lead time management
- ✅ Soft delete functionality
- ✅ Search and filter by category, name, SKU
- ✅ Pagination support

### Inventory Management
- ✅ Real-time stock tracking via ledger system
- ✅ Automatic inventory updates on sales
- ✅ Manual stock adjustments with reason tracking
- ✅ Transaction history per product
- ✅ Low stock alerts based on reorder points
- ✅ Balance calculation with running totals
- ✅ Prevents negative inventory
- ✅ Transaction types: SALE, PURCHASE, RETURN, ADJUST

### Sales Management
- ✅ Point-of-sale interface
- ✅ Single and bulk sales entry
- ✅ Multiple payment modes: Cash, Card, UPI, NetBanking, Wallet
- ✅ Automatic discount and GST calculation (12% GST)
- ✅ Invoice number generation
- ✅ Customer phone tracking
- ✅ Sales history with date filtering
- ✅ CSV bulk upload support
- ✅ Print invoice functionality

### Demand Forecasting
- ✅ Exponential smoothing algorithm
- ✅ 90-day historical lookback
- ✅ Forecast horizons: 4w, 8w, 12w (or custom days)
- ✅ Confidence intervals (95%)
- ✅ Average daily demand calculation
- ✅ Peak demand identification
- ✅ Recommended reorder quantity
- ✅ Visual forecast charts

### Analytics & Reporting
- ✅ Revenue trends (daily aggregation)
- ✅ Top products by revenue, quantity, or transactions
- ✅ Category breakdown with percentage analysis
- ✅ ABC inventory classification
- ✅ Summary KPIs: Total revenue, units sold, transactions, best seller
- ✅ Customizable time periods (7, 30, 90 days)
- ✅ Visual charts and graphs

### User Management
- ✅ JWT authentication
- ✅ User registration and login
- ✅ Password hashing with bcrypt
- ✅ Role-based access: Superuser vs Regular user
- ✅ Last login tracking
- ✅ Protected routes
- ✅ 30-minute token expiration (configurable)

---

## 3. Technology Stack

### Backend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | FastAPI | 0.104.1 | REST API framework |
| **Server** | Uvicorn | 0.24.0 | ASGI server |
| **ORM** | SQLAlchemy | 2.0.23 | Database ORM |
| **Database** | PostgreSQL | 15 | Primary database |
| **Cache** | Redis | 7-alpine | Caching layer |
| **Authentication** | python-jose | 3.3.0 | JWT tokens |
| **Password Hashing** | passlib[bcrypt] | 1.7.4 | Password security |
| **Validation** | Pydantic | 2.5.0 | Data validation |
| **Data Processing** | Pandas | 2.1.3 | Data manipulation |
| **Forecasting** | NumPy | 1.26.2 | Numerical compute |
| **Advanced Forecasting** | Prophet | 1.1.5 | Time series forecasting |
| **Testing** | Pytest | 7.4.3 | Testing framework |

### Frontend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | React | 18.3.1 | UI library |
| **Build Tool** | Vite | 5.1.0 | Fast build tool |
| **Routing** | React Router | 6.22.0 | Client-side routing |
| **HTTP Client** | Axios | 1.6.7 | API requests |
| **Styling** | Tailwind CSS | 3.4.1 | Utility-first CSS |
| **Charts** | Recharts | 2.12.0 | Data visualization |
| **Icons** | Lucide React | 0.263.1 | Icon library |
| **UI Components** | Headless UI | 1.7.18 | Accessible components |

### DevOps
- **Containerization**: Docker & Docker Compose
- **Version Control**: Git
- **Environment Management**: python-dotenv
- **Migrations**: Alembic

---

## 4. System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: 4 GB minimum, 8 GB recommended
- **Storage**: 5 GB free space
- **CPU**: Dual-core processor (2.0 GHz+)

### Software Prerequisites

#### Option 1: Docker (Recommended)
- Docker Desktop 4.0+
- Docker Compose 2.0+

#### Option 2: Local Development
- **Python**: 3.9 or higher (3.11 recommended)
- **Node.js**: 18.x or higher (20.x recommended)
- **PostgreSQL**: 15.x or higher
- **Redis**: 7.x or higher
- **Git**: Latest version

### Package Managers
- **Python**: pip or conda
- **Node.js**: npm or yarn

---

## 5. Installation & Setup

### Option A: Docker Setup (Recommended)

#### Step 1: Clone the Repository
```bash
git clone https://github.com/your-org/garb-and-glitz-inventory.git
cd garb-and-glitz-inventory
```

#### Step 2: Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# For Docker, default values usually work
```

#### Step 3: Build and Run
```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

#### Step 4: Initialize Database
```bash
# Run database setup script
docker-compose exec backend python setup_database.py
```

#### Step 5: Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Login Credentials**:
  - Username: `admin`
  - Password: `admin123`

---

### Option B: Local Development Setup

#### Step 1: Clone Repository
```bash
git clone https://github.com/your-org/garb-and-glitz-inventory.git
cd garb-and-glitz-inventory
```

#### Step 2: Setup PostgreSQL Database
```bash
# Using PostgreSQL CLI
createdb garb_glitz_inventory

# Or using psql
psql -U postgres
CREATE DATABASE garb_glitz_inventory;
\q
```

#### Step 3: Setup Redis
```bash
# Install Redis (macOS with Homebrew)
brew install redis
brew services start redis

# Install Redis (Ubuntu)
sudo apt-get install redis-server
sudo systemctl start redis

# Install Redis (Windows)
# Download from: https://github.com/microsoftarchive/redis/releases
```

#### Step 4: Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example ../.env
# Edit .env with your database credentials

# Run database setup
python setup_database.py

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Step 5: Frontend Setup
```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Configure environment
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env

# Start development server
npm run dev
```

#### Step 6: Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 6. Running the Application

### Development Mode

#### Using Docker
```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up --build
```

#### Local Development
```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: PostgreSQL (if not running as service)
postgres -D /usr/local/var/postgres

# Terminal 4: Redis (if not running as service)
redis-server
```

### Production Mode

#### Using Docker
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d
```

#### Manual Deployment
```bash
# Backend
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# Frontend
cd frontend
npm run build
# Serve dist/ folder with Nginx or similar
```

---

## 7. Project Structure

```
garb-and-glitz-inventory/
├── backend/                          # Python FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app initialization
│   │   ├── config.py                 # Configuration settings
│   │   ├── auth.py                   # JWT authentication
│   │   ├── dependencies.py           # Database session management
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── auth.py           # Auth endpoints
│   │   │       ├── products.py       # Product CRUD
│   │   │       ├── sales.py          # Sales endpoints
│   │   │       ├── inventory.py      # Inventory management
│   │   │       ├── forecasting.py    # Demand forecasting
│   │   │       ├── analytics.py      # Analytics & reports
│   │   │       └── suppliers.py      # Supplier management
│   │   ├── models/
│   │   │   ├── base.py               # SQLAlchemy base
│   │   │   ├── users.py              # User model
│   │   │   ├── products.py           # Product model
│   │   │   ├── suppliers.py          # Supplier model
│   │   │   ├── sales.py              # Sale model
│   │   │   ├── inventory_ledger.py   # Inventory tracking
│   │   │   └── ...
│   │   ├── schemas/
│   │   │   ├── products.py           # Product schemas
│   │   │   ├── sales.py              # Sale schemas
│   │   │   ├── inventory.py          # Inventory schemas
│   │   │   └── ...
│   │   └── services/
│   │       ├── analytics_service.py
│   │       └── inventory_service.py
│   ├── tests/
│   ├── setup_database.py             # Database initialization
│   ├── reset_admin_password.py       # Password reset utility
│   ├── requirements.txt              # Python dependencies
│   └── Dockerfile
│
├── frontend/                         # React frontend
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js             # Axios API client
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   │   └── ProtectedRoute.jsx
│   │   │   ├── layout/
│   │   │   │   ├── Layout.jsx
│   │   │   │   ├── Navbar.jsx
│   │   │   │   └── Sidebar.jsx
│   │   │   └── common/
│   │   │       ├── Button.jsx
│   │   │       ├── Card.jsx
│   │   │       ├── Modal.jsx
│   │   │       └── ...
│   │   ├── pages/
│   │   │   ├── Auth/
│   │   │   │   └── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Products/
│   │   │   │   ├── ProductList.jsx
│   │   │   │   ├── ProductForm.jsx
│   │   │   │   └── ProductDetail.jsx
│   │   │   ├── Sales/
│   │   │   │   ├── NewSale.jsx
│   │   │   │   └── SalesHistory.jsx
│   │   │   ├── Inventory/
│   │   │   │   └── StockView.jsx
│   │   │   ├── Analytics/
│   │   │   │   └── AnalyticsDashboard.jsx
│   │   │   └── Forecasting/
│   │   │       ├── ForecastDashboard.jsx
│   │   │       └── ForecastChart.jsx
│   │   ├── App.jsx                   # Main routing
│   │   └── main.jsx                  # React entry point
│   ├── package.json                  # Node.js dependencies
│   ├── vite.config.js                # Vite configuration
│   ├── tailwind.config.js            # Tailwind configuration
│   └── Dockerfile
│
├── docker-compose.yml                # Docker orchestration
├── .env.example                      # Environment template
├── README_LATEST.md                  # This file
└── CODE_WORKS.md                     # Code flow documentation
```

---

## 8. Environment Configuration

### Backend Environment Variables (.env)

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/garb_glitz_inventory
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=garb_glitz_inventory

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# JWT Authentication
SECRET_KEY=your-super-secret-key-min-32-characters-long
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# Application Settings
ENVIRONMENT=development  # development, staging, or production
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
MAX_UPLOAD_SIZE=10485760  # 10MB in bytes

# CORS Settings (comma-separated)
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend Environment Variables (.env)

```bash
# API Configuration
VITE_API_URL=http://localhost:8000/api/v1

# Application Metadata
VITE_APP_NAME=Garb & Glitz Inventory
VITE_APP_VERSION=1.0.0
```

### Security Notes

⚠️ **IMPORTANT**:
- Never commit `.env` files to version control
- Use strong SECRET_KEY (32+ characters)
- Change default admin password after first login
- Use environment-specific configurations
- Enable HTTPS in production
- Restrict CORS origins in production

---

## 9. Database Setup

### Schema Overview

#### Tables
1. **users** - User accounts with authentication
2. **products** - Product catalog with SKUs
3. **suppliers** - Supplier information
4. **sales** - Sales transactions
5. **inventory_ledger** - Inventory movement tracking
6. **purchase_orders** - Purchase order management
7. **returns** - Product returns and refunds
8. **promotions** - Promotional campaigns
9. **calendar_events** - Event tracking

### Running Migrations

```bash
# Using Alembic (if migrations exist)
cd backend
alembic upgrade head

# Or run the setup script
python setup_database.py
```

### Database Setup Script

The `setup_database.py` script:
- ✅ Drops all existing tables (WARNING: Data loss!)
- ✅ Creates fresh database schema
- ✅ Creates admin user (username: `admin`, password: `admin123`)
- ✅ Creates 4 sample suppliers
- ✅ Creates 80 sample products (20 per category)
- ✅ Generates 6 months of sales data
- ✅ Initializes inventory ledger

```bash
cd backend
python setup_database.py
```

### Reset Admin Password

If you forget the admin password:

```bash
cd backend
python reset_admin_password.py
```

This resets the admin password to `admin123`.

### Manual Database Connection

```bash
# Connect to PostgreSQL
psql -U postgres -d garb_glitz_inventory

# Useful queries
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM sales;
SELECT * FROM users;
```

---

## 10. API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Authentication

All protected endpoints require JWT Bearer token in the header:

```bash
Authorization: Bearer <your_jwt_token>
```

### Key Endpoints

#### Authentication
```bash
POST   /api/v1/auth/login       # Login and get JWT token
POST   /api/v1/auth/register    # Register new user
GET    /api/v1/auth/me          # Get current user info
```

#### Products
```bash
GET    /api/v1/products          # List products (paginated)
POST   /api/v1/products          # Create product
GET    /api/v1/products/{sku}    # Get product by SKU
PUT    /api/v1/products/{sku}    # Update product
DELETE /api/v1/products/{sku}    # Soft delete product
```

#### Sales
```bash
POST   /api/v1/sales             # Create sale
POST   /api/v1/sales/bulk        # Bulk upload sales (CSV)
GET    /api/v1/sales             # List sales
GET    /api/v1/sales/{sale_id}   # Get sale details
```

#### Inventory
```bash
GET    /api/v1/inventory                # Current stock levels
POST   /api/v1/inventory/adjust         # Adjust inventory
GET    /api/v1/inventory/ledger/{sku}   # Transaction history
GET    /api/v1/inventory/low-stock      # Low stock alerts
```

#### Forecasting
```bash
GET    /api/v1/forecast          # Generate forecast
  ?sku=SAR001&horizon=4w
```

#### Analytics
```bash
GET    /api/v1/summary           # Summary KPIs
GET    /api/v1/top-products      # Top products
GET    /api/v1/revenue-trend     # Revenue trend
GET    /api/v1/category-breakdown # Sales by category
GET    /api/v1/abc-analysis      # ABC classification
```

### Example Requests

#### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

#### Create Product
```bash
curl -X POST "http://localhost:8000/api/v1/products" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "SAR120",
    "name": "Banarasi Silk Saree",
    "category": "Saree",
    "cost_price": 2000,
    "sell_price": 3500
  }'
```

#### Create Sale
```bash
curl -X POST "http://localhost:8000/api/v1/sales" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "SAR001",
    "quantity": 2,
    "unit_price": 1500,
    "payment_mode": "UPI"
  }'
```

---

## 11. Frontend Pages

### Login Page (`/login`)
- Username/password authentication
- JWT token storage
- Error handling
- Redirect to dashboard on success

### Dashboard (`/`)
- Today's revenue card
- Total SKUs count
- Low stock alerts
- Revenue trend chart (30 days)
- Top 5 products table
- Quick actions

### Product Management (`/products`)
- **Product List**: Searchable, filterable table with pagination
- **Create Product**: Modal form with validation
- **Edit Product**: In-place editing
- **Product Details**: Detailed view with sales history

### Sales Management (`/sales`)
- **New Sale**: POS interface with cart functionality
- **Sales History**: Filterable transaction list

### Inventory (`/inventory`)
- Current stock levels
- Low stock filtering
- Manual stock adjustment
- Transaction history per product

### Analytics (`/analytics`)
- Time period selector (7/30/90 days)
- Revenue and sales KPIs
- Top 10 products table
- Category breakdown charts

### Forecasting (`/forecast`)
- Product selector
- Forecast horizon selector (4w/8w/12w)
- Forecast visualization chart
- Demand metrics and recommendations

---

## 12. Authentication

### JWT Token Flow

1. User submits credentials to `/api/v1/auth/login`
2. Backend validates credentials
3. Backend generates JWT token (30-minute expiry)
4. Frontend stores token in `localStorage`
5. Frontend includes token in all API requests
6. Backend validates token on protected endpoints
7. Token expires → User redirected to login

### Password Security

- **Hashing**: bcrypt with automatic salting
- **Truncation**: 72-byte limit for bcrypt compatibility
- **Validation**: Email format validation on registration

### Protected Routes

All routes except `/login` are protected with `ProtectedRoute` wrapper:

```jsx
<Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
  {/* All child routes are protected */}
</Route>
```

### Role-Based Access

- **Regular User**: Access to all features
- **Superuser**: Additional access to user management

---

## 13. Deployment

### Production Checklist

- [ ] Update SECRET_KEY to strong random value
- [ ] Set ENVIRONMENT=production
- [ ] Configure proper ALLOWED_ORIGINS (no wildcards)
- [ ] Enable HTTPS
- [ ] Set secure database credentials
- [ ] Configure Redis with authentication
- [ ] Set up database backups
- [ ] Configure logging and monitoring
- [ ] Run security audit
- [ ] Set up CI/CD pipeline
- [ ] Configure reverse proxy (Nginx)
- [ ] Set resource limits (CPU, memory)

### Recommended Production Stack

- **Database**: PostgreSQL with connection pooling
- **Cache**: Redis with persistence
- **Backend**: Gunicorn + Uvicorn workers
- **Frontend**: Nginx serving static build
- **Reverse Proxy**: Nginx
- **HTTPS**: Let's Encrypt SSL certificates
- **Process Manager**: systemd or PM2
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack or Loki

---

## 14. Troubleshooting

### Common Issues

#### Backend won't start
```bash
# Check PostgreSQL connection
psql -U postgres -d garb_glitz_inventory

# Check Redis connection
redis-cli ping

# Verify dependencies
pip list

# Check logs
docker-compose logs backend
```

#### Frontend can't connect to backend
```bash
# Verify VITE_API_URL in .env
cat frontend/.env

# Check CORS settings in backend
# backend/app/main.py - CORSMiddleware configuration

# Test API directly
curl http://localhost:8000/health
```

#### Database migration errors
```bash
# Drop and recreate database
psql -U postgres
DROP DATABASE garb_glitz_inventory;
CREATE DATABASE garb_glitz_inventory;
\q

# Run setup script
python backend/setup_database.py
```

#### Login fails after password reset
```bash
# Reset admin password
cd backend
python reset_admin_password.py

# Or manually update in database
psql -U postgres -d garb_glitz_inventory
UPDATE users SET hashed_password = 'new_hash' WHERE username = 'admin';
```

#### Bcrypt errors
```bash
# Ensure bcrypt version 4.1.2 (not 5.x)
pip install bcrypt==4.1.2

# Restart backend server
```

### Debug Mode

Enable detailed logging:

```python
# backend/app/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 15. Contributing

### Development Workflow

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and test thoroughly
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Create Pull Request

### Code Standards

- **Python**: Follow PEP 8
- **JavaScript**: ESLint configuration
- **Commits**: Conventional Commits format
- **Testing**: Write tests for new features

---

## 16. License

This project is proprietary software. All rights reserved.

---

## Quick Start Commands

```bash
# Clone and setup
git clone <repo-url>
cd garb-and-glitz-inventory
cp .env.example .env

# Docker (Recommended)
docker-compose up -d
docker-compose exec backend python setup_database.py

# Local Development
# Terminal 1 - Backend
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python setup_database.py
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend && npm install && npm run dev

# Access
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# Login:    admin / admin123
```

---

## Support

For issues, questions, or contributions:
- **Documentation**: See CODE_WORKS.md for detailed code flow
- **API Docs**: http://localhost:8000/docs
- **Issues**: GitHub Issues

---

**Built with ❤️ for Garb & Glitz**
