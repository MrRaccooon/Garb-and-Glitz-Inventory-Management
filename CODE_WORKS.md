# CODE_WORKS - Complete Code Flow Documentation

## Table of Contents

### 1.0 Introduction
- 1.1 Purpose of This Document
- 1.2 How to Use This Guide
- 1.3 System Architecture Overview

### 2.0 Authentication System
- 2.1 Login Flow (Frontend → Backend → Database)
- 2.2 Token Management
- 2.3 Protected Routes
- 2.4 Logout Flow

### 3.0 Product Management
- 3.1 Add Product Flow
- 3.2 Edit Product Flow
- 3.3 View Products Flow
- 3.4 Delete/Deactivate Product Flow

### 4.0 Sales Management
- 4.1 Create Sale Flow
- 4.2 View Sales History Flow
- 4.3 Sales Analytics Flow

### 5.0 Inventory Management
- 5.1 View Stock Flow
- 5.2 Inventory Updates (Automated via Sales)
- 5.3 Low Stock Alerts

### 6.0 Forecasting System
- 6.1 Demand Forecast Flow
- 6.2 Forecasting Algorithm (Exponential Smoothing)
- 6.3 Chart Visualization

### 7.0 Analytics & Reports
- 7.1 Dashboard Summary Flow
- 7.2 Top Products Analysis
- 7.3 Category Breakdown

### 8.0 Import Relationships
- 8.1 Frontend Imports Map
- 8.2 Backend Imports Map
- 8.3 Shared Dependencies

### 9.0 Data Structures & Algorithms
- 9.1 Exponential Smoothing Algorithm
- 9.2 ABC Analysis Algorithm
- 9.3 Inventory Ledger System
- 9.4 Data Structures Used

### 10.0 Database Schema & Relationships
- 10.1 Table Relationships
- 10.2 Foreign Keys
- 10.3 Indexes

---

# 1.0 Introduction

## 1.1 Purpose of This Document

This document explains **exactly** how the Garb & Glitz Inventory System works from a code perspective. When you click a button in the frontend, this guide shows you:
- Where that click is handled
- What function gets called
- How the data travels through the code
- Which API endpoint is hit
- How the backend processes the request
- What database operations occur
- How the response comes back

## 1.2 How to Use This Guide

Each section follows this pattern:
1. **User Action** - What you click/do in the UI
2. **Frontend Code** - Where it starts and what happens
3. **API Call** - How the request is made
4. **Backend Route** - Which endpoint handles it
5. **Business Logic** - What processing happens
6. **Database Operation** - What gets read/written
7. **Response Flow** - How data comes back to the UI

## 1.3 System Architecture Overview

```
┌─────────────────┐
│   React Frontend │ (Port 3000)
│   (Vite + React) │
└────────┬────────┘
         │
         │ HTTP Requests (Axios)
         │
         ▼
┌─────────────────┐
│  FastAPI Backend │ (Port 8000)
│   (Python)      │
└────────┬────────┘
         │
         │ SQLAlchemy ORM
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │ (Port 5432)
│    Database     │
└─────────────────┘
```

**Key Technologies:**
- **Frontend**: React 18, Vite, TailwindCSS, Axios, React Router
- **Backend**: FastAPI, SQLAlchemy, Pydantic, JWT (python-jose), bcrypt
- **Database**: PostgreSQL 15
- **Caching**: Redis (for future optimizations)

---

# 2.0 Authentication System

## 2.1 Login Flow (Frontend → Backend → Database)

### USER ACTION: Click "Sign In" Button

**File**: `frontend/src/pages/Auth/Login.jsx`

#### Step 1: User Enters Credentials and Clicks "Sign In"

```
Location: frontend/src/pages/Auth/Login.jsx
Lines: 26-54
```

**What Happens:**
1. User fills in username and password fields (lines 82-109)
2. User clicks "Sign In" button (line 112-128)
3. Form submission triggers `handleSubmit` function (line 26)

**Code Flow:**
```javascript
const handleSubmit = async (e) => {
  e.preventDefault();  // Prevent page reload
  setError('');        // Clear any previous errors
  setLoading(true);    // Show loading spinner

  // Make API call
  const response = await api.post('/auth/login', {
    username: formData.username,
    password: formData.password
  });
```

**Key Variables:**
- `formData.username` - Username entered by user
- `formData.password` - Password entered by user
- `loading` - Boolean state to show/hide spinner
- `error` - String to display error messages

---

#### Step 2: API Client Intercepts Request

```
Location: frontend/src/api/client.js
Lines: 12-24 (Request Interceptor)
```

**What Happens:**
1. Axios request interceptor catches the POST request
2. Logs the request to console: `🚀 API Request: POST http://127.0.0.1:8000/api/v1/auth/login`
3. Checks for existing access_token in localStorage (not present for login)
4. Sets Content-Type header to 'application/json'
5. Sends request to backend

**Important Code:**
```javascript
apiClient.interceptors.request.use(
  (config) => {
    console.log('🚀 API Request:', config.method.toUpperCase(), config.baseURL + config.url);
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;  // Not added for login
    }
    return config;
  }
);
```

**API Endpoint Called**: `POST http://127.0.0.1:8000/api/v1/auth/login`

**Request Body**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

---

#### Step 3: Backend Receives Request

```
Location: backend/app/api/v1/auth.py
Lines: 27-64 (login endpoint)
```

**What Happens:**
1. FastAPI router receives POST request at `/api/v1/auth/login`
2. Pydantic validates request body against `LoginRequest` schema
3. `login()` function is called with validated data
4. Database session is injected via `Depends(get_db)`

**Code:**
```python
@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,  # Auto-validated by Pydantic
    db: Session = Depends(get_db)  # Database session injected
):
```

**Pydantic Schema** (`app/schemas/auth.py`):
```python
class LoginRequest(BaseModel):
    username: str
    password: str
```

---

#### Step 4: Authentication Logic

```
Location: backend/app/auth.py
Lines: 77-96 (authenticate_user function)
```

**What Happens:**
1. `authenticate_user()` is called with username and password
2. Database is queried for user with matching username
3. Password is verified using bcrypt
4. User's `is_active` status is checked

**Code:**
```python
def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    # Query database for user
    user = db.query(User).filter(User.username == username.lower()).first()

    if not user:
        return None  # User not found

    if not verify_password(password, user.hashed_password):
        return None  # Password doesn't match

    if not user.is_active:
        return None  # Account is disabled

    return user  # Authentication successful
```

---

#### Step 5: Password Verification

```
Location: backend/app/auth.py
Lines: 24-37 (verify_password function)
```

**What Happens:**
1. Plain text password is converted to bytes
2. Truncated to 72 bytes (bcrypt limit)
3. Bcrypt compares with stored hash

**Code:**
```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Truncate password to 72 bytes for bcrypt compatibility
    plain_password_bytes = plain_password.encode('utf-8')[:72]
    return pwd_context.verify(plain_password_bytes, hashed_password)
```

**Database Query** (SQLAlchemy ORM):
```sql
SELECT * FROM users
WHERE username = 'admin'
LIMIT 1;
```

**Database Table**: `users`
- `user_id` - Primary key
- `username` - Unique, indexed
- `hashed_password` - Bcrypt hash
- `is_active` - Boolean
- `is_superuser` - Boolean
- `last_login` - Timestamp

---

#### Step 6: JWT Token Creation

```
Location: backend/app/auth.py
Lines: 55-74 (create_access_token function)
```

**What Happens:**
1. Token expiration time is calculated (30 minutes from now)
2. JWT payload is created with username and expiration
3. Token is signed using SECRET_KEY from settings
4. `last_login` timestamp is updated in database

**Code:**
```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
```

**JWT Payload**:
```json
{
  "sub": "admin",
  "exp": 1700000000
}
```

**Token Properties**:
- Algorithm: HS256
- Expiration: 30 minutes
- Secret Key: From `settings.SECRET_KEY` (environment variable)

---

#### Step 7: Database Update - Last Login

```
Location: backend/app/api/v1/auth.py
Lines: 53-55
```

**What Happens:**
1. User's `last_login` field is updated with current UTC time
2. Database session commits the change

**Code:**
```python
# Update last login
user.last_login = datetime.utcnow()
db.commit()
```

**SQL Executed**:
```sql
UPDATE users
SET last_login = '2024-01-15 10:30:45'
WHERE user_id = 1;
```

---

#### Step 8: Response Sent to Frontend

```
Location: backend/app/api/v1/auth.py
Lines: 57-64
```

**What Happens:**
1. Access token and token type are packaged into response
2. Pydantic serializes response to JSON
3. FastAPI returns HTTP 200 OK

**Code:**
```python
access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
access_token = create_access_token(
    data={"sub": user.username}, expires_delta=access_token_expires
)

logger.info(f"User {user.username} logged in successfully")

return {"access_token": access_token, "token_type": "bearer"}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

#### Step 9: Frontend Receives Response

```
Location: frontend/src/api/client.js
Lines: 27-31 (Response Interceptor)
```

**What Happens:**
1. Axios response interceptor catches successful response
2. Logs to console: `✅ API Response: /auth/login 200`
3. Returns response to calling code

**Code:**
```javascript
apiClient.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.config.url, response.status);
    return response;
  }
);
```

---

#### Step 10: Token Storage and Redirect

```
Location: frontend/src/pages/Auth/Login.jsx
Lines: 37-41
```

**What Happens:**
1. Access token is extracted from response
2. Token is saved to browser's localStorage
3. User is redirected to dashboard ("/")
4. Loading spinner is hidden

**Code:**
```javascript
// Store the token in localStorage
localStorage.setItem('access_token', response.data.access_token);

// Redirect to dashboard
navigate('/');
```

**localStorage Contents**:
```
Key: "access_token"
Value: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### Login Flow - Complete Summary

```
┌──────────────────────────────────────────────────────────────┐
│                    LOGIN FLOW DIAGRAM                        │
└──────────────────────────────────────────────────────────────┘

1. USER ACTION
   └─> Enter username/password in Login.jsx (Lines 82-109)
   └─> Click "Sign In" button (Line 112)

2. FRONTEND PROCESSING (Login.jsx)
   └─> handleSubmit() triggered (Line 26)
   └─> setLoading(true) - Show spinner
   └─> Call api.post('/auth/login', credentials) (Line 32)

3. API CLIENT (client.js)
   └─> Request interceptor logs request (Line 14)
   └─> Sets Content-Type header (Line 6)
   └─> Sends HTTP POST to backend (Line 4)

4. BACKEND ROUTE (api/v1/auth.py)
   └─> FastAPI receives POST /api/v1/auth/login (Line 27)
   └─> Pydantic validates LoginRequest
   └─> Database session injected
   └─> login() function called (Line 28)

5. AUTHENTICATION (auth.py)
   └─> authenticate_user() called (Line 45)
   └─> Query database for user (Line 89)
      SQL: SELECT * FROM users WHERE username = 'admin'
   └─> verify_password() with bcrypt (Line 92)
      ├─> Convert password to bytes (Line 36)
      ├─> Truncate to 72 bytes
      └─> Compare with hashed_password
   └─> Check is_active status (Line 94)

6. TOKEN GENERATION (auth.py)
   └─> create_access_token() called (Line 58)
   └─> Calculate expiration (30 min) (Line 70)
   └─> Create JWT payload with username (Line 72)
   └─> Sign with SECRET_KEY using HS256 (Line 73)

7. DATABASE UPDATE (api/v1/auth.py)
   └─> Update last_login timestamp (Line 54)
      SQL: UPDATE users SET last_login = NOW() WHERE user_id = 1
   └─> Commit transaction (Line 55)

8. BACKEND RESPONSE (api/v1/auth.py)
   └─> Return Token response (Line 64)
   └─> JSON: {"access_token": "...", "token_type": "bearer"}
   └─> HTTP Status: 200 OK

9. FRONTEND RECEIVES RESPONSE (client.js)
   └─> Response interceptor logs success (Line 29)
   └─> Returns data to Login.jsx

10. TOKEN STORAGE & REDIRECT (Login.jsx)
    └─> Extract access_token from response (Line 38)
    └─> Save to localStorage (Line 38)
    └─> Navigate to dashboard "/" (Line 41)
    └─> setLoading(false) - Hide spinner

11. USER IS NOW LOGGED IN
    └─> All subsequent requests include token in header
    └─> Protected routes are accessible
    └─> Token expires in 30 minutes
```

---

## 2.2 Token Management

### How Tokens Are Used in Subsequent Requests

After login, every API request includes the JWT token in the Authorization header.

**Request Interceptor** (`frontend/src/api/client.js` Line 15-17):
```javascript
const token = localStorage.getItem('access_token');
if (token) {
  config.headers.Authorization = `Bearer ${token}`;
}
```

**Backend Token Validation** (`backend/app/auth.py` Lines 99-141):
```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    # Decode JWT token
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    username: str = payload.get("sub")

    # Get user from database
    user = db.query(User).filter(User.username == username).first()

    # Check if user exists and is active
    if not user or not user.is_active:
        raise HTTPException(status_code=401)

    return user
```

### Token Expiration Handling

**Response Interceptor** (`frontend/src/api/client.js` Lines 37-40):
```javascript
if (status === 401) {
  localStorage.removeItem('access_token');
  window.location.href = '/login';
  console.error('Unauthorized - redirecting to login');
}
```

---

## 2.3 Protected Routes

**File**: `frontend/src/components/ProtectedRoute.jsx`

```javascript
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('access_token');

  if (!token) {
    // No token found - redirect to login
    return <Navigate to="/login" replace />;
  }

  // Token exists - render protected content
  return children;
};
```

**Usage** (`frontend/src/App.jsx`):
```javascript
<Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
  <Route index element={<Dashboard />} />
  <Route path="products" element={<ProductList />} />
  <Route path="sales" element={<SalesHistory />} />
  // ... all protected routes
</Route>
```

---

## 2.4 Logout Flow

**File**: `frontend/src/components/layout/Navbar.jsx`

```javascript
const handleLogout = () => {
  // Remove token from localStorage
  localStorage.removeItem('access_token');

  // Redirect to login page
  navigate('/login');
};
```

**When User Clicks Logout Button:**
1. Token is removed from localStorage
2. User is redirected to /login
3. Protected routes become inaccessible
4. Next API request will fail with 401
5. Response interceptor catches 401 and redirects to login

---

# 3.0 Product Management

## 3.1 Add Product Flow (Frontend → Backend → Database)

### USER ACTION: Click "Add Product" Button

**Location**: User navigates to Products page and clicks "Add New Product"

#### Step 1: User Clicks "Add New Product" Button

```
Location: frontend/src/pages/Products/ProductList.jsx
```

**What Happens:**
1. User is on the Products page viewing list of products
2. User clicks "Add New Product" button
3. `ProductForm` component is shown in modal/separate view
4. Form is initialized with empty fields

---

#### Step 2: User Fills Out Product Form

```
Location: frontend/src/pages/Products/ProductForm.jsx
Lines: 19-33 (formData state)
```

**Form Fields:**

**Required Fields:**
- `sku` - Product SKU (Format: ABC123 - 3 letters + 3 digits)
- `name` - Product name
- `category` - Category (Saree, Suit, Lehenga, Dupatta)
- `costPrice` - Cost price in INR
- `sellPrice` - Selling price in INR

**Optional Fields:**
- `subcategory` - Subcategory (depends on category selected)
- `brand` - Brand name
- `size` - Size (Free Size, S, M, L, etc.)
- `color` - Color
- `fabric` - Fabric type
- `reorderPoint` - Minimum stock level (default: 10)
- `leadTimeDays` - Days to receive stock after ordering (default: 7)
- `supplierId` - Supplier ID (selected from dropdown)

**Form State:**
```javascript
const [formData, setFormData] = useState({
  sku: '',
  name: '',
  category: 'Saree',
  subcategory: '',
  brand: '',
  size: '',
  color: '',
  fabric: '',
  costPrice: '',
  sellPrice: '',
  reorderPoint: '10',
  leadTimeDays: '7',
  supplierId: ''
});
```

---

#### Step 3: Real-Time Field Validation

```
Location: frontend/src/pages/Products/ProductForm.jsx
Lines: 77-101 (validateField function)
Lines: 103-134 (handleChange function)
```

**What Happens:**
1. As user types, `handleChange` is triggered on each keystroke
2. Field value is updated in state
3. `validateField` is called for that specific field
4. Error message is set if validation fails

**Validation Rules:**
```javascript
SKU Validation:
- Must match pattern: /^[A-Z]{3}[0-9]{3}$/
- Example: SAR001, LEH123, SUI045
- Auto-converts to uppercase

Name Validation:
- Required field
- Cannot be empty

Price Validation:
- Must be greater than 0
- Sell price cannot be less than cost price

Numbers Validation:
- reorderPoint and leadTimeDays must be positive
```

**Example Validation:**
```javascript
const validateField = (name, value) => {
  switch (name) {
    case 'sku':
      if (!value) return 'SKU is required';
      if (!/^[A-Z]{3}[0-9]{3}$/.test(value)) {
        return 'SKU must be 3 uppercase letters followed by 3 digits';
      }
      return '';
    // ... other validations
  }
};
```

---

#### Step 4: Fetch Suppliers for Dropdown

```
Location: frontend/src/pages/Products/ProductForm.jsx
Lines: 40-55 (useEffect - fetchSuppliers)
```

**What Happens:**
1. On component mount, `useEffect` triggers
2. API call is made to GET /suppliers
3. Suppliers are loaded into dropdown
4. User can select a supplier (optional)

**Code:**
```javascript
useEffect(() => {
  const fetchSuppliers = async () => {
    try {
      setLoadingSuppliers(true);
      const response = await axios.get('/suppliers');
      setSuppliers(response.data);
    } catch (error) {
      console.error('Failed to fetch suppliers:', error);
    } finally {
      setLoadingSuppliers(false);
    }
  };

  fetchSuppliers();
}, []);
```

**API Call**: `GET http://127.0.0.1:8000/api/v1/suppliers`

---

#### Step 5: User Clicks "Create Product" Button

```
Location: frontend/src/pages/Products/ProductForm.jsx
Lines: 157-272 (handleSubmit function)
```

**What Happens:**
1. Form submission triggers `handleSubmit`
2. All fields are validated using `validateForm()`
3. If validation fails, alert is shown and submission stops
4. If validation passes, payload is built from formData
5. API request is made to create product

**Validation Check:**
```javascript
const handleSubmit = async (e) => {
  e.preventDefault();

  if (!validateForm()) {
    alert('Please fix all validation errors before submitting');
    return;
  }

  // Proceed with API call...
```

---

#### Step 6: Build API Payload

```
Location: frontend/src/pages/Products/ProductForm.jsx
Lines: 168-204
```

**What Happens:**
1. Payload object is created with only non-empty values
2. Field names are converted to snake_case for backend
3. Numbers are parsed to correct types
4. Optional fields are only included if they have values

**Payload Building Code:**
```javascript
const payload = {
  sku: formData.sku.trim(),
  name: formData.name.trim(),
  category: formData.category,
  cost_price: parseFloat(formData.costPrice),
  sell_price: parseFloat(formData.sellPrice),
  reorder_point: parseInt(formData.reorderPoint) || 10,
  lead_time_days: parseInt(formData.leadTimeDays) || 7,
  active: true
};

// Add optional fields only if they have values
if (formData.subcategory && formData.subcategory.trim()) {
  payload.subcategory = formData.subcategory.trim();
}

if (formData.supplierId) {
  payload.supplier_id = formData.supplierId;
}
```

**Example Payload:**
```json
{
  "sku": "SAR001",
  "name": "Red Silk Saree",
  "category": "Saree",
  "subcategory": "Silk",
  "brand": "Kanjivaram",
  "size": "Free Size",
  "color": "Red",
  "fabric": "Silk",
  "cost_price": 5000.00,
  "sell_price": 7500.00,
  "reorder_point": 10,
  "lead_time_days": 7,
  "supplier_id": "SUP001",
  "active": true
}
```

---

#### Step 7: Make API Call to Backend

```
Location: frontend/src/pages/Products/ProductForm.jsx
Lines: 210-217
```

**What Happens:**
1. `axios.post('/products', payload)` is called
2. Request interceptor adds Authorization header with JWT token
3. POST request is sent to backend

**Code:**
```javascript
let response;
if (mode === 'create') {
  console.log('POST /products');
  response = await axios.post('/products', payload);
} else {
  console.log(`PUT /products/${formData.sku}`);
  response = await axios.put(`/products/${formData.sku}`, payload);
}
```

**API Endpoint**: `POST http://127.0.0.1:8000/api/v1/products`

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

---

#### Step 8: Backend Receives Request

```
Location: backend/app/api/v1/products.py
Lines: 55-121 (create_product endpoint)
```

**What Happens:**
1. FastAPI router receives POST request at `/api/v1/products`
2. Pydantic validates request body against `ProductCreate` schema
3. Database session is injected
4. `create_product()` function is called

**Code:**
```python
@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,  # Validated by Pydantic
    db: Session = Depends(get_db)  # Database session injected
) -> ProductResponse:
```

**Pydantic Schema** (`app/schemas/products.py`):
```python
class ProductCreate(BaseModel):
    sku: str
    name: str
    category: str
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    fabric: Optional[str] = None
    cost_price: float
    sell_price: float
    reorder_point: int = 10
    lead_time_days: int = 7
    supplier_id: Optional[str] = None
    active: bool = True
```

---

#### Step 9: Backend Validation Checks

```
Location: backend/app/api/v1/products.py
Lines: 64-87
```

**What Happens:**
1. Check if SKU already exists in database
2. Validate sell_price >= cost_price
3. If supplier_id provided, validate supplier exists
4. If any validation fails, HTTPException is raised

**Validation Code:**
```python
# Check if SKU already exists
existing = db.query(Product).filter(Product.sku == product.sku).first()
if existing:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Product with SKU '{product.sku}' already exists"
    )

# Validate business logic
if product.sell_price < product.cost_price:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Sell price cannot be less than cost price"
    )

# Validate supplier_id if provided
if product.supplier_id:
    from app.models.suppliers import Supplier
    supplier = db.query(Supplier).filter(Supplier.supplier_id == product.supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Supplier with ID '{product.supplier_id}' not found"
        )
```

**SQL Queries Executed:**
```sql
-- Check for existing SKU
SELECT * FROM products WHERE sku = 'SAR001' LIMIT 1;

-- Validate supplier (if supplier_id provided)
SELECT * FROM suppliers WHERE supplier_id = 'SUP001' LIMIT 1;
```

---

#### Step 10: Insert Product into Database

```
Location: backend/app/api/v1/products.py
Lines: 89-96
```

**What Happens:**
1. New `Product` model instance is created
2. Product is added to database session
3. Session is committed (transaction finalized)
4. Product is refreshed to get generated fields
5. Success is logged

**Code:**
```python
# Create new product
db_product = Product(**product.model_dump())
db.add(db_product)
db.commit()
db.refresh(db_product)

logger.info(f"Product created successfully: {db_product.sku}")
return db_product
```

**SQL Executed:**
```sql
INSERT INTO products (
  sku, name, category, subcategory, brand, size, color, fabric,
  cost_price, sell_price, reorder_point, lead_time_days,
  supplier_id, active, created_at
) VALUES (
  'SAR001', 'Red Silk Saree', 'Saree', 'Silk', 'Kanjivaram',
  'Free Size', 'Red', 'Silk', 5000.00, 7500.00, 10, 7,
  'SUP001', true, '2024-01-15 10:30:45'
);
```

**Database Table**: `products`
- `sku` - Primary key (VARCHAR)
- `name` - Product name (VARCHAR)
- `category` - Category (VARCHAR)
- `subcategory` - Subcategory (VARCHAR, nullable)
- `brand` - Brand (VARCHAR, nullable)
- `size` - Size (VARCHAR, nullable)
- `color` - Color (VARCHAR, nullable)
- `fabric` - Fabric (VARCHAR, nullable)
- `cost_price` - Cost price (DECIMAL)
- `sell_price` - Selling price (DECIMAL)
- `reorder_point` - Reorder threshold (INTEGER)
- `lead_time_days` - Lead time (INTEGER)
- `supplier_id` - Foreign key to suppliers (VARCHAR, nullable)
- `active` - Soft delete flag (BOOLEAN)
- `created_at` - Timestamp (TIMESTAMP)

---

#### Step 11: Response Sent to Frontend

```
Location: backend/app/api/v1/products.py
Line: 96
```

**What Happens:**
1. Product object is serialized to JSON by Pydantic
2. HTTP 201 Created status is returned
3. Response includes all product fields

**Response:**
```json
{
  "sku": "SAR001",
  "name": "Red Silk Saree",
  "category": "Saree",
  "subcategory": "Silk",
  "brand": "Kanjivaram",
  "size": "Free Size",
  "color": "Red",
  "fabric": "Silk",
  "cost_price": 5000.00,
  "sell_price": 7500.00,
  "reorder_point": 10,
  "lead_time_days": 7,
  "supplier_id": "SUP001",
  "active": true,
  "created_at": "2024-01-15T10:30:45"
}
```

---

#### Step 12: Frontend Receives Success Response

```
Location: frontend/src/pages/Products/ProductForm.jsx
Lines: 219-223
```

**What Happens:**
1. Response is received with status 201
2. Success alert is shown to user
3. `onSuccess()` callback is triggered
4. Modal/form is closed
5. Product list is refreshed

**Code:**
```javascript
console.log('=== SUCCESS ===');
console.log('Response:', response.data);

alert(`Product ${mode === 'create' ? 'created' : 'updated'} successfully!`);
if (onSuccess) onSuccess();
```

---

### Add Product Flow - Complete Summary

```
┌──────────────────────────────────────────────────────────────┐
│                 ADD PRODUCT FLOW DIAGRAM                     │
└──────────────────────────────────────────────────────────────┘

1. USER ACTION
   └─> Navigate to Products page
   └─> Click "Add New Product" button
   └─> ProductForm component is displayed

2. FORM INITIALIZATION (ProductForm.jsx)
   └─> useEffect fetches suppliers (Line 40)
      API: GET /suppliers
   └─> Form fields initialized with empty/default values (Line 19)
   └─> Suppliers loaded into dropdown (Line 45)

3. USER FILLS FORM
   └─> User types in fields
   └─> handleChange() triggered on each keystroke (Line 103)
   └─> SKU auto-converted to uppercase (Line 108)
   └─> validateField() checks field in real-time (Line 77)
   └─> Error messages shown if validation fails

4. USER SUBMITS FORM
   └─> Click "Create Product" button (Line 514)
   └─> handleSubmit() triggered (Line 157)
   └─> validateForm() checks all required fields (Line 136)
   └─> If invalid, alert shown and stop (Line 161)

5. BUILD PAYLOAD (ProductForm.jsx)
   └─> Create payload object (Line 169)
   └─> Convert camelCase to snake_case
   └─> Parse numbers: parseFloat, parseInt
   └─> Include only non-empty optional fields (Line 181-204)

6. API CALL (ProductForm.jsx)
   └─> axios.post('/products', payload) (Line 213)
   └─> Request interceptor adds JWT token (client.js Line 16)
   └─> POST http://127.0.0.1:8000/api/v1/products

7. BACKEND ROUTE (api/v1/products.py)
   └─> FastAPI receives POST /products (Line 55)
   └─> Pydantic validates ProductCreate schema
   └─> Database session injected via Depends(get_db)
   └─> create_product() function called (Line 56)

8. BACKEND VALIDATION (api/v1/products.py)
   └─> Check if SKU already exists (Line 65)
      SQL: SELECT * FROM products WHERE sku = 'SAR001'
   └─> Validate sell_price >= cost_price (Line 73)
   └─> Validate supplier_id if provided (Line 80)
      SQL: SELECT * FROM suppliers WHERE supplier_id = 'SUP001'
   └─> If validation fails, raise HTTPException

9. DATABASE INSERT (api/v1/products.py)
   └─> Create Product model instance (Line 90)
   └─> db.add(db_product) - Add to session (Line 91)
   └─> db.commit() - Commit transaction (Line 92)
      SQL: INSERT INTO products (...) VALUES (...)
   └─> db.refresh(db_product) - Get generated fields (Line 93)
   └─> Log success (Line 95)

10. BACKEND RESPONSE (api/v1/products.py)
    └─> Return ProductResponse (Line 96)
    └─> Pydantic serializes to JSON
    └─> HTTP Status: 201 Created

11. FRONTEND SUCCESS (ProductForm.jsx)
    └─> Response received (Line 219)
    └─> Show success alert (Line 222)
    └─> Call onSuccess() callback (Line 223)
    └─> Close form/modal
    └─> Refresh product list

12. PRODUCT NOW EXISTS
    └─> Product is in database
    └─> Visible in product list
    └─> Can be used in sales transactions
    └─> Inventory can be tracked
```

---

# 4.0 Sales Management

Sales transactions are the core of the inventory system. When a sale is made, it automatically updates inventory levels via the ledger system.

## 4.1 Create Sale Flow

**Primary Files:**
- Backend API: `backend/app/api/v1/sales.py`
- Frontend Display: `frontend/src/pages/Sales/SalesHistory.jsx`
- Models: `backend/app/models/sales.py`, `backend/app/models/inventory.py`

**Note:** Sales are created via API calls (potentially through bulk upload, POS system, or direct API integration). The system focuses on recording and tracking sales data.

### Step-by-Step Flow:

**1. API REQUEST** (`POST /api/v1/sales`)

**Request Body:**
```json
{
  "sku": "SAR001",
  "quantity": 5,
  "unit_price": 299.00,
  "payment_mode": "CARD"
}
```

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**2. BACKEND ROUTE** (`backend/app/api/v1/sales.py:37`)

```python
@router.post("/sales", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
async def create_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db)
) -> SaleResponse:
```

**Pydantic Schema Validation** (`backend/app/schemas/sales.py`):
```python
class SaleCreate(BaseModel):
    sku: str = Field(..., min_length=3, max_length=50)
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    payment_mode: str = Field(..., regex="^(CASH|CARD|UPI)$")
```

**3. PRODUCT VERIFICATION** (`sales.py:46`)

```python
# Verify product exists
product = db.query(Product).filter(Product.sku == sale.sku).first()
if not product:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Product with SKU '{sale.sku}' not found"
    )
```

**SQL Executed:**
```sql
SELECT * FROM products WHERE sku = 'SAR001' LIMIT 1;
```

**4. STOCK LEVEL CHECK** (`sales.py:53`)

```python
# Check current stock level from inventory ledger
current_stock = db.query(func.sum(InventoryLedger.change_qty))\
    .filter(InventoryLedger.sku == sale.sku)\
    .scalar() or 0

if current_stock < sale.quantity:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Insufficient stock. Available: {current_stock}, Requested: {sale.quantity}"
    )
```

**SQL Executed:**
```sql
SELECT SUM(change_qty) FROM inventory_ledger WHERE sku = 'SAR001';
```

**Example:**
- Current stock: 100 units
- Requested: 5 units
- Check passes (100 >= 5)

**5. CALCULATE TOTAL & CREATE SALE** (`sales.py:62`)

```python
# Calculate total
total = sale.unit_price * sale.quantity  # 299.00 * 5 = 1495.00

# Generate unique invoice number
invoice_number = f"INV-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{sale.sku[:4]}"
# Example: "INV-20250116143022-SAR0"

# Create sale record
db_sale = Sale(
    timestamp=datetime.utcnow(),
    sku=sale.sku,
    quantity=sale.quantity,
    unit_price=sale.unit_price,
    total=total,
    payment_mode=sale.payment_mode,
    invoice_number=invoice_number
)
db.add(db_sale)
db.flush()  # Flush to get the sale_id before committing
```

**SQL Executed:**
```sql
INSERT INTO sales (timestamp, sku, quantity, unit_price, total, payment_mode, invoice_number)
VALUES ('2025-01-16 14:30:22', 'SAR001', 5, 299.00, 1495.00, 'CARD', 'INV-20250116143022-SAR0');
```

**6. UPDATE INVENTORY LEDGER** (`sales.py:78`)

```python
# Create inventory ledger entry (negative change for sale)
new_balance = current_stock - sale.quantity  # 100 - 5 = 95

ledger_entry = InventoryLedger(
    sku=sale.sku,
    change_qty=-sale.quantity,  # Negative for sales
    balance_qty=new_balance,
    reason=f"Sale {db_sale.invoice_number}",
    timestamp=datetime.utcnow()
)
db.add(ledger_entry)
```

**SQL Executed:**
```sql
INSERT INTO inventory_ledger (sku, change_qty, balance_qty, reason, timestamp)
VALUES ('SAR001', -5, 95, 'Sale INV-20250116143022-SAR0', '2025-01-16 14:30:22');
```

**7. COMMIT TRANSACTION** (`sales.py:86`)

```python
db.commit()
db.refresh(db_sale)
```

Both the sale record and inventory ledger entry are committed atomically.

**8. RETURN RESPONSE** (`sales.py:89`)

```python
return db_sale  # FastAPI serializes to SaleResponse
```

**Response (201 Created):**
```json
{
  "sale_id": 123,
  "timestamp": "2025-01-16T14:30:22",
  "sku": "SAR001",
  "quantity": 5,
  "unit_price": 299.00,
  "total": 1495.00,
  "payment_mode": "CARD",
  "invoice_number": "INV-20250116143022-SAR0"
}
```

### Complete Flow Diagram:

```
API REQUEST
   └─> POST /sales with { sku, quantity, unit_price, payment_mode }
   └─> JWT token in Authorization header

1. BACKEND ROUTE (sales.py Line 37)
   └─> create_sale() function called
   └─> Pydantic validates SaleCreate schema
   └─> Database session injected

2. PRODUCT VERIFICATION (sales.py Line 46)
   └─> Query: SELECT * FROM products WHERE sku = 'SAR001'
   └─> If not found → 404 error
   └─> If found → continue

3. STOCK LEVEL CHECK (sales.py Line 53)
   └─> Query: SELECT SUM(change_qty) FROM inventory_ledger WHERE sku = 'SAR001'
   └─> Calculate current_stock
   └─> If current_stock < quantity → 400 error (insufficient stock)
   └─> If current_stock >= quantity → continue

4. CALCULATE TOTAL (sales.py Line 62)
   └─> total = unit_price * quantity
   └─> Generate invoice_number with timestamp

5. CREATE SALE RECORD (sales.py Line 67)
   └─> Create Sale model instance
   └─> db.add(db_sale)
   └─> db.flush() - get sale_id before commit
   └─> INSERT INTO sales (...)

6. UPDATE INVENTORY LEDGER (sales.py Line 78)
   └─> Calculate new_balance = current_stock - quantity
   └─> Create InventoryLedger entry with negative change_qty
   └─> reason = "Sale {invoice_number}"
   └─> db.add(ledger_entry)
   └─> INSERT INTO inventory_ledger (...)

7. COMMIT TRANSACTION (sales.py Line 86)
   └─> db.commit() - atomic commit of both records
   └─> db.refresh(db_sale)

8. RETURN RESPONSE
   └─> Return SaleResponse with sale_id, timestamp, invoice_number
   └─> HTTP 201 Created

RESULT:
   └─> Sale recorded in database
   └─> Inventory automatically reduced
   └─> Invoice number generated
   └─> Transaction traceable via ledger
```

### Key Features:

**Atomic Transaction:**
Both the sale record and inventory ledger update are committed together. If either fails, both are rolled back.

**Inventory Ledger System:**
Every sale creates a ledger entry with:
- `change_qty`: -5 (negative for sales, positive for purchases)
- `balance_qty`: 95 (new stock level after sale)
- `reason`: "Sale INV-20250116143022-SAR0" (traceability)

**Validation Chain:**
1. Pydantic validates request format
2. Product existence check
3. Stock availability check
4. Only then create sale

**Invoice Generation:**
Format: `INV-YYYYMMDDHHMMSS-SKUX`
- Timestamp ensures uniqueness
- SKU prefix for quick identification

---

## 4.2 View Sales History Flow

**File**: `frontend/src/pages/Sales/SalesHistory.jsx`

**When User Navigates to /sales:**

**1. COMPONENT MOUNT** (`SalesHistory.jsx:15`)

```javascript
useEffect(() => {
  fetchSales();
}, []);
```

Component mounts and immediately fetches sales data.

**2. FETCH SALES FUNCTION** (`SalesHistory.jsx:49`)

```javascript
const fetchSales = async () => {
  setLoading(true);
  try {
    const params = {};
    if (startDate) params.start_date = startDate;  // Optional filter
    if (endDate) params.end_date = endDate;        // Optional filter

    const response = await api.get('/sales', { params });
    setSales(response.data);
  } catch (error) {
    alert('Failed to fetch sales: ' + (error.response?.data?.detail || error.message));
  } finally {
    setLoading(false);
  }
};
```

**3. API REQUEST**

```
GET /api/v1/sales?start_date=2025-01-01&end_date=2025-01-16
Authorization: Bearer <JWT_TOKEN>
```

**4. BACKEND ROUTE** (`backend/app/api/v1/sales.py:18`)

```python
@router.get("/sales", response_model=List[SaleResponse])
async def get_sales(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> List[SaleResponse]:
    query = db.query(Sale)

    if start_date:
        query = query.filter(Sale.timestamp >= start_date)
    if end_date:
        query = query.filter(Sale.timestamp <= end_date)

    sales = query.order_by(Sale.timestamp.desc()).all()
    return sales
```

**SQL Executed:**
```sql
SELECT * FROM sales
WHERE timestamp >= '2025-01-01' AND timestamp <= '2025-01-16'
ORDER BY timestamp DESC;
```

**5. FRONTEND DISPLAY** (`SalesHistory.jsx:99`)

```javascript
<table className="min-w-full">
  <thead>
    <tr>
      <th>Invoice</th>
      <th>Date & Time</th>
      <th>SKU</th>
      <th>Product Name</th>
      <th>Quantity</th>
      <th>Unit Price</th>
      <th>Total</th>
      <th>Payment</th>
    </tr>
  </thead>
  <tbody>
    {sales.map((sale) => (
      <tr key={sale.sale_id}>
        <td>{sale.invoice_number}</td>
        <td>{formatDateTime(sale.timestamp)}</td>
        <td>{sale.sku}</td>
        <td>{getProductName(sale.sku)}</td>
        <td>{sale.quantity}</td>
        <td>{formatCurrency(sale.unit_price)}</td>
        <td>{formatCurrency(sale.total)}</td>
        <td>
          <span className={`badge ${getPaymentBadgeColor(sale.payment_mode)}`}>
            {sale.payment_mode}
          </span>
        </td>
      </tr>
    ))}
  </tbody>
</table>
```

**6. DATE FILTERING** (`SalesHistory.jsx:29`)

User can filter by date range:
```javascript
const handleFilter = () => {
  fetchSales();  // Re-fetches with startDate and endDate params
};
```

### Flow Diagram:

```
USER NAVIGATES TO /sales
   └─> SalesHistory component mounts

1. USEEFFECT TRIGGERS (Line 15)
   └─> fetchSales() called

2. API REQUEST (Line 59)
   └─> GET /sales?start_date=...&end_date=...
   └─> JWT token added by interceptor

3. BACKEND ROUTE (sales.py Line 18)
   └─> get_sales() function
   └─> Optional date filters applied
   └─> Query database

4. DATABASE QUERY
   └─> SELECT * FROM sales WHERE timestamp BETWEEN ... ORDER BY timestamp DESC

5. BACKEND RESPONSE
   └─> Return List[SaleResponse]
   └─> HTTP 200 OK

6. FRONTEND UPDATE (Line 61)
   └─> setSales(response.data)
   └─> Component re-renders

7. TABLE DISPLAY (Line 99)
   └─> Map over sales array
   └─> Render each row with formatted data
   └─> Show invoice, date, SKU, quantity, total, payment

USER SEES:
   └─> Complete sales history table
   └─> Filterable by date range
   └─> Sortable columns
   └─> Payment mode badges
```

---

# 6.0 Forecasting System

The forecasting system uses **exponential smoothing** algorithm to predict future demand based on historical sales data. It provides demand forecasts with 95% confidence intervals.

## 6.1 Demand Forecast Flow

**Primary Files:**
- Frontend: `frontend/src/pages/Forecasting/ForecastDashboard.jsx`
- Backend API: `backend/app/api/v1/forecasting.py`
- Algorithm: Exponential Smoothing with confidence intervals

### Step-by-Step Flow:

**When User Navigates to /forecasting:**

**1. COMPONENT MOUNT** (`ForecastDashboard.jsx:15`)

```javascript
useEffect(() => {
  fetchSkus();
}, []);

const fetchSkus = async () => {
  const response = await api.get('/products');
  const activeSkus = response.data
    .filter(item => item.active !== false)
    .map(item => ({ sku: item.sku, name: item.name }));
  setSkus(activeSkus);

  if (activeSkus.length > 0) {
    setSelectedSku(activeSkus[0].sku);  // Pre-select first SKU
  }
};
```

Component loads and fetches all active products to populate the SKU dropdown.

**2. USER SELECTS PARAMETERS** (`ForecastDashboard.jsx:84`)

User interface provides:
- **SKU Dropdown**: Select product to forecast
- **Horizon Buttons**: Choose 4w, 8w, or 12w (weeks)
- **Get Forecast Button**: Trigger forecast generation

```javascript
const [selectedSku, setSelectedSku] = useState('');
const [horizon, setHorizon] = useState('4w');  // Default 4 weeks

<select value={selectedSku} onChange={(e) => setSelectedSku(e.target.value)}>
  {skus.map(item => (
    <option key={item.sku} value={item.sku}>
      {item.name} ({item.sku})
    </option>
  ))}
</select>

<button onClick={() => setHorizon('4w')}>4w</button>
<button onClick={() => setHorizon('8w')}>8w</button>
<button onClick={() => setHorizon('12w')}>12w</button>
```

**3. USER CLICKS "GET FORECAST"** (`ForecastDashboard.jsx:38`)

```javascript
const getForecast = async () => {
  if (!selectedSku) {
    alert('Please select a SKU');
    return;
  }

  setLoading(true);
  try {
    const response = await api.get('/forecast', {
      params: {
        sku: selectedSku,
        horizon: horizon
      }
    });
    setForecastData(response.data);
  } catch (error) {
    alert('Failed to fetch forecast: ' + (error.response?.data?.detail || error.message));
  } finally {
    setLoading(false);
  }
};
```

**4. API REQUEST**

```
GET /api/v1/forecast?sku=SAR001&horizon=4w
Authorization: Bearer <JWT_TOKEN>
```

**5. BACKEND ROUTE** (`backend/app/api/v1/forecasting.py:75`)

```python
@router.get("/forecast", response_model=ForecastResponse)
async def get_demand_forecast(
    sku: str = Query(..., description="Product SKU to forecast"),
    horizon: str = Query("4w", regex="^[1-9][0-9]*[wd]$", description="Forecast horizon"),
    db: Session = Depends(get_db)
) -> ForecastResponse:
```

**Query Parameters Validated:**
- `sku`: Required string (product SKU)
- `horizon`: Format `<number><w|d>` (e.g., "4w" = 4 weeks, "30d" = 30 days)

**6. PRODUCT VERIFICATION** (`forecasting.py:100`)

```python
product = db.query(Product).filter(Product.sku == sku).first()
if not product:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Product with SKU '{sku}' not found"
    )
```

**SQL Executed:**
```sql
SELECT * FROM products WHERE sku = 'SAR001' LIMIT 1;
```

**7. PARSE HORIZON** (`forecasting.py:108`)

```python
unit = horizon[-1]          # 'w' or 'd'
value = int(horizon[:-1])   # numeric part

# Convert to days
horizon_days = value * 7 if unit == 'w' else value
# Example: '4w' → 4 * 7 = 28 days

if horizon_days > 365:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Forecast horizon cannot exceed 365 days"
    )
```

**8. FETCH HISTORICAL SALES DATA** (`forecasting.py:126`)

```python
# Get last 90 days of sales data
lookback_date = datetime.utcnow() - timedelta(days=90)

sales_data = db.query(
    func.date(Sale.timestamp).label('sale_date'),
    func.sum(Sale.quantity).label('total_quantity')
).filter(
    Sale.sku == sku,
    Sale.timestamp >= lookback_date
).group_by(
    func.date(Sale.timestamp)
).order_by(
    func.date(Sale.timestamp)
).all()
```

**SQL Executed:**
```sql
SELECT
  DATE(timestamp) AS sale_date,
  SUM(quantity) AS total_quantity
FROM sales
WHERE sku = 'SAR001'
  AND timestamp >= '2024-10-16'
GROUP BY DATE(timestamp)
ORDER BY DATE(timestamp);
```

**Example Result:**
```
sale_date    | total_quantity
-------------|---------------
2024-10-16   | 5
2024-10-17   | 8
2024-10-18   | 3
...          | ...
2025-01-16   | 12
```

**9. RUN FORECASTING ALGORITHM** (`forecasting.py:151`)

```python
historical_data = [(row.sale_date, float(row.total_quantity)) for row in sales_data]

forecast_data = calculate_forecast(historical_data, horizon_days)
```

**10. EXPONENTIAL SMOOTHING ALGORITHM** (`forecasting.py:18`)

This is the core DSA implementation:

```python
def calculate_forecast(sales_data: list, horizon_days: int) -> list[ForecastDataPoint]:
    if not sales_data:
        return []

    # Extract quantities from (date, quantity) tuples
    quantities = [qty for _, qty in sales_data]

    # SMOOTHING PARAMETER
    alpha = 0.3  # Weight for recent observations (0 < alpha < 1)
                 # Higher alpha = more weight on recent data

    # STEP 1: Calculate baseline (historical average)
    baseline = np.mean(quantities)
    # Example: [5, 8, 3, 7, 12, ...] → baseline = 7.5

    # STEP 2: Calculate standard deviation for confidence intervals
    std_dev = np.std(quantities) if len(quantities) > 1 else baseline * 0.2
    # Example: std_dev = 3.2

    # STEP 3: Initialize forecasting
    forecast = []
    current_date = sales_data[-1][0]  # Last observed date
    last_value = quantities[-1]        # Last observed quantity
    smoothed_value = last_value

    # STEP 4: Generate forecast for each future day
    for day in range(1, horizon_days + 1):
        forecast_date = current_date + timedelta(days=day)

        # Apply exponential smoothing with trend adjustment
        if len(quantities) > 1:
            # Calculate linear trend
            trend = (quantities[-1] - quantities[0]) / len(quantities)
            # Example: (12 - 5) / 90 = 0.078 units/day

            # Exponential smoothing formula:
            # S_t = α * X_t + (1 - α) * (S_t-1 + T)
            smoothed_value = alpha * last_value + (1 - alpha) * (smoothed_value + trend)
            # Example: 0.3 * 12 + 0.7 * (8 + 0.078) = 9.25
        else:
            smoothed_value = baseline

        # STEP 5: Calculate 95% confidence intervals
        # Margin increases with forecast distance (sqrt(day))
        margin = 1.96 * std_dev * np.sqrt(day)
        # Example day 1: 1.96 * 3.2 * sqrt(1) = 6.27
        # Example day 28: 1.96 * 3.2 * sqrt(28) = 33.19

        # Create forecast point
        forecast.append(ForecastDataPoint(
            date=forecast_date,
            value=round(max(0, smoothed_value), 2),           # Point estimate
            lower_bound=round(max(0, smoothed_value - margin), 2),  # Lower 95% CI
            upper_bound=round(smoothed_value + margin, 2)     # Upper 95% CI
        ))

    return forecast
```

**Algorithm Explanation:**

1. **Exponential Smoothing**: Weighs recent observations more heavily than older ones
   - Formula: `S_t = α * X_t + (1 - α) * (S_t-1 + T)`
   - `α = 0.3`: 30% weight on most recent value, 70% on smoothed history
   - Trend adjustment accounts for increasing/decreasing demand patterns

2. **Confidence Intervals**: Uncertainty grows with forecast distance
   - 95% CI = Forecast ± (1.96 * std_dev * sqrt(days_ahead))
   - Near-term forecasts have narrow intervals
   - Far-future forecasts have wide intervals

3. **Trend Detection**: Linear trend calculated from first to last observation
   - Positive trend: Demand is increasing
   - Negative trend: Demand is decreasing
   - Zero trend: Demand is stable

**11. BUILD RESPONSE** (`forecasting.py:157`)

```python
historical_quantities = [qty for _, qty in historical_data]
avg_daily_sales = np.mean(historical_quantities)

return ForecastResponse(
    sku=sku,
    product_name=product.name,
    forecast_horizon_days=horizon_days,
    forecast=forecast_data,  # List of 28 ForecastDataPoint objects
    historical_avg_daily_sales=round(avg_daily_sales, 2),
    confidence_level=0.95
)
```

**12. FRONTEND RECEIVES RESPONSE** (`ForecastDashboard.jsx:52`)

```javascript
setForecastData(response.data);
```

**Response Example:**
```json
{
  "sku": "SAR001",
  "product_name": "Saree - Silk",
  "forecast_horizon_days": 28,
  "historical_avg_daily_sales": 7.5,
  "confidence_level": 0.95,
  "forecast": [
    {
      "date": "2025-01-17",
      "value": 9.25,
      "lower_bound": 3.0,
      "upper_bound": 15.5
    },
    {
      "date": "2025-01-18",
      "value": 9.33,
      "lower_bound": 0.5,
      "upper_bound": 18.2
    },
    // ... 26 more days
  ]
}
```

**13. DISPLAY FORECAST CHART** (`ForecastDashboard.jsx:137`)

```javascript
{forecastData && (
  <>
    <Card className="p-6 mb-6">
      <h2>Forecast for {selectedProduct?.name || selectedSku}</h2>
      <ForecastChart data={forecastData.forecast} />
    </Card>

    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <Card>
        <div>Average Daily Demand</div>
        <div>{metrics.avgDailyDemand}</div>
      </Card>

      <Card>
        <div>Peak Demand</div>
        <div>{metrics.peakDemand}</div>
      </Card>

      <Card>
        <div>Recommended Reorder Qty</div>
        <div>{metrics.recommendedReorder}</div>
      </Card>
    </div>
  </>
)}
```

**14. CALCULATE METRICS** (`ForecastDashboard.jsx:61`)

```javascript
const calculateMetrics = () => {
  const forecastValues = forecastData.forecast.map(d => d.value).filter(v => v != null);
  const avgDailyDemand = forecastValues.reduce((a, b) => a + b, 0) / forecastValues.length;
  const peakDemand = Math.max(...forecastValues);
  const recommendedReorder = Math.ceil(avgDailyDemand * 7 * 1.5);  // 1.5 weeks supply

  return {
    avgDailyDemand: avgDailyDemand.toFixed(2),
    peakDemand: peakDemand.toFixed(2),
    recommendedReorder
  };
};
```

**Example Metrics:**
- **Average Daily Demand**: 9.3 units/day (average of forecast values)
- **Peak Demand**: 15.8 units (max forecasted value)
- **Recommended Reorder Qty**: 98 units (9.3 * 7 * 1.5 = 1.5 weeks supply)

### Complete Flow Diagram:

```
USER NAVIGATES TO /forecasting
   └─> ForecastDashboard component mounts

1. FETCH ACTIVE PRODUCTS (Line 19)
   └─> GET /products
   └─> Filter active products
   └─> Populate SKU dropdown

2. USER SELECTS PARAMETERS
   └─> Select SKU from dropdown (e.g., SAR001)
   └─> Select horizon (4w, 8w, or 12w)
   └─> Click "Get Forecast"

3. API REQUEST (Line 46)
   └─> GET /forecast?sku=SAR001&horizon=4w
   └─> JWT token added by interceptor

4. BACKEND ROUTE (forecasting.py Line 75)
   └─> get_demand_forecast() function
   └─> Validate sku and horizon parameters

5. PRODUCT VERIFICATION (Line 100)
   └─> Query: SELECT * FROM products WHERE sku = 'SAR001'
   └─> If not found → 404 error

6. PARSE HORIZON (Line 108)
   └─> Extract number and unit ('4w' → 28 days)
   └─> Validate <= 365 days

7. FETCH HISTORICAL DATA (Line 129)
   └─> Query last 90 days of sales
   └─> SELECT DATE(timestamp), SUM(quantity) FROM sales ...
   └─> Group by date, order by date
   └─> If no data → 400 error

8. RUN FORECASTING ALGORITHM (Line 151)
   └─> calculate_forecast(historical_data, 28)

9. EXPONENTIAL SMOOTHING (forecasting.py Line 18)
   └─> Extract quantities from historical data
   └─> Calculate baseline = mean(quantities)
   └─> Calculate std_dev for confidence intervals
   └─> Initialize smoothed_value = last observed value
   └─> FOR each day in forecast horizon (1 to 28):
       ├─> Calculate trend = (last - first) / count
       ├─> Apply smoothing: α * last + (1-α) * (smoothed + trend)
       ├─> Calculate margin = 1.96 * std_dev * sqrt(day)
       ├─> Create ForecastDataPoint:
       │   ├─> date: future date
       │   ├─> value: smoothed forecast
       │   ├─> lower_bound: forecast - margin
       │   └─> upper_bound: forecast + margin
       └─> Append to forecast list

10. BUILD RESPONSE (Line 157)
    └─> Calculate avg_daily_sales from historical data
    └─> Return ForecastResponse with:
        ├─> sku, product_name
        ├─> forecast_horizon_days
        ├─> forecast (28 data points)
        ├─> historical_avg_daily_sales
        └─> confidence_level (0.95)

11. FRONTEND UPDATE (ForecastDashboard Line 52)
    └─> setForecastData(response.data)
    └─> Component re-renders

12. CALCULATE METRICS (Line 61)
    └─> avgDailyDemand = mean of forecast values
    └─> peakDemand = max forecast value
    └─> recommendedReorder = avgDaily * 7 * 1.5

13. DISPLAY (Line 137)
    └─> Render ForecastChart with line graph
    └─> Show 3 metric cards:
        ├─> Average Daily Demand
        ├─> Peak Demand
        └─> Recommended Reorder Qty

USER SEES:
   └─> Interactive forecast chart with confidence bands
   └─> 28-day demand predictions
   └─> Key metrics for inventory planning
   └─> Recommended reorder quantities
```

### Key Algorithm Details:

**Exponential Smoothing Formula:**
```
S_t = α * X_t + (1 - α) * (S_t-1 + T)

Where:
- S_t = Smoothed forecast at time t
- X_t = Last observed value
- α = 0.3 (smoothing constant)
- T = Linear trend adjustment
- S_t-1 = Previous smoothed value
```

**Confidence Interval Formula:**
```
95% CI = Forecast ± 1.96 * σ * sqrt(h)

Where:
- 1.96 = Z-score for 95% confidence
- σ = Historical standard deviation
- h = Forecast horizon (days ahead)
- sqrt(h) = Uncertainty grows with square root of distance
```

**Trend Calculation:**
```
Trend = (Last_Quantity - First_Quantity) / Number_of_Days

Example:
- 90 days of data: first day = 5 units, last day = 12 units
- Trend = (12 - 5) / 90 = 0.078 units/day (increasing demand)
```

---

# 7.0 Analytics & Reports

The analytics system provides comprehensive business intelligence including revenue analysis, top products, category breakdowns, and ABC classification.

## 7.1 Analytics Dashboard Flow

**Primary Files:**
- Frontend: `frontend/src/pages/Analytics/AnalyticsDashboard.jsx`
- Backend API: `backend/app/api/v1/analytics.py`

### Step-by-Step Flow:

**When User Navigates to /analytics:**

**1. COMPONENT MOUNT** (`AnalyticsDashboard.jsx:13`)

```javascript
const [days, setDays] = useState(30);  // Default 30 days

useEffect(() => {
  fetchAnalytics();
}, [days]);  // Re-fetch when days changes
```

Component mounts and fetches analytics for the default 30-day period.

**2. FETCH ANALYTICS** (`AnalyticsDashboard.jsx:17`)

```javascript
const fetchAnalytics = async () => {
  setLoading(true);
  try {
    // Fetch summary
    const summaryRes = await api.get('/summary', {
      params: { days }
    });
    setSummary(summaryRes.data);

    // Fetch top products
    const topProductsRes = await api.get('/top-products', {
      params: { days, limit: 10, sort_by: 'revenue' }
    });
    setTopProducts(topProductsRes.data);

    // Fetch category breakdown
    const categoryRes = await api.get('/category-breakdown', {
      params: { days }
    });
    setCategoryBreakdown(categoryRes.data);

  } catch (error) {
    alert('Failed to fetch analytics: ' + (error.response?.data?.detail || error.message));
  } finally {
    setLoading(false);
  }
};
```

**Three parallel API calls made:**
1. Summary statistics
2. Top 10 products by revenue
3. Category breakdown

**3. SUMMARY API** (`backend/app/api/v1/analytics.py:280`)

```python
@router.get("/summary")
async def get_analytics_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
) -> dict:
    # Calculate date range
    start_date = datetime.utcnow() - timedelta(days=days)

    # Query sales data
    sales = db.query(Sale).filter(Sale.timestamp >= start_date).all()

    if not sales:
        return {
            "total_revenue": 0,
            "total_units_sold": 0,
            "total_transactions": len(sales),
            "unique_products_sold": 0,
            "avg_order_value": 0,
            "avg_daily_revenue": 0,
            "best_selling_product": None
        }

    # Calculate metrics
    total_revenue = sum(sale.total for sale in sales)
    total_units = sum(sale.quantity for sale in sales)
    unique_products = len(set(sale.sku for sale in sales))
    avg_order = total_revenue / len(sales) if sales else 0
    avg_daily_revenue = total_revenue / days

    # Find best selling product by quantity
    product_sales = {}
    for sale in sales:
        if sale.sku not in product_sales:
            product_sales[sale.sku] = 0
        product_sales[sale.sku] += sale.quantity

    best_sku = max(product_sales.items(), key=lambda x: x[1])[0] if product_sales else None
    best_product = db.query(Product).filter(Product.sku == best_sku).first() if best_sku else None

    return {
        "total_revenue": float(total_revenue),
        "total_units_sold": total_units,
        "total_transactions": len(sales),
        "unique_products_sold": unique_products,
        "avg_order_value": float(avg_order),
        "avg_daily_revenue": float(avg_daily_revenue),
        "best_selling_product": {
            "sku": best_product.sku,
            "name": best_product.name,
            "quantity": product_sales[best_sku]
        } if best_product else None
    }
```

**SQL Executed:**
```sql
-- Fetch all sales in date range
SELECT * FROM sales WHERE timestamp >= '2024-12-17';

-- Then fetch best selling product
SELECT * FROM products WHERE sku = 'SAR001';
```

**4. TOP PRODUCTS API** (`analytics.py:20`)

```python
@router.get("/top-products", response_model=List[TopProductResponse])
async def get_top_products(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("revenue", regex="^(revenue|quantity|transactions)$"),
    db: Session = Depends(get_db)
) -> List[TopProductResponse]:

    start_date = datetime.utcnow() - timedelta(days=days)

    # Query with JOIN to get product details
    results = db.query(
        Sale.sku,
        Product.name,
        Product.category,
        func.sum(Sale.total).label('total_revenue'),
        func.sum(Sale.quantity).label('total_quantity'),
        func.count(Sale.sale_id).label('transaction_count')
    ).join(
        Product, Sale.sku == Product.sku
    ).filter(
        Sale.timestamp >= start_date
    ).group_by(
        Sale.sku,
        Product.name,
        Product.category
    )

    # Sort based on parameter
    if sort_by == "revenue":
        results = results.order_by(desc('total_revenue'))
    elif sort_by == "quantity":
        results = results.order_by(desc('total_quantity'))
    else:  # transactions
        results = results.order_by(desc('transaction_count'))

    results = results.limit(limit).all()

    return [
        TopProductResponse(
            sku=row.sku,
            name=row.name,
            category=row.category,
            total_revenue=float(row.total_revenue),
            total_quantity=int(row.total_quantity),
            transaction_count=int(row.transaction_count)
        )
        for row in results
    ]
```

**SQL Executed:**
```sql
SELECT
  sales.sku,
  products.name,
  products.category,
  SUM(sales.total) AS total_revenue,
  SUM(sales.quantity) AS total_quantity,
  COUNT(sales.sale_id) AS transaction_count
FROM sales
JOIN products ON sales.sku = products.sku
WHERE sales.timestamp >= '2024-12-17'
GROUP BY sales.sku, products.name, products.category
ORDER BY total_revenue DESC
LIMIT 10;
```

**5. CATEGORY BREAKDOWN API** (`analytics.py:102`)

```python
@router.get("/category-breakdown", response_model=List[CategoryBreakdownResponse])
async def get_category_breakdown(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
) -> List[CategoryBreakdownResponse]:

    start_date = datetime.utcnow() - timedelta(days=days)

    # Query category sales
    results = db.query(
        Product.category,
        func.sum(Sale.total).label('revenue'),
        func.sum(Sale.quantity).label('quantity'),
        func.count(func.distinct(Sale.sku)).label('unique_products'),
        func.count(Sale.sale_id).label('transaction_count')
    ).join(
        Product, Sale.sku == Product.sku
    ).filter(
        Sale.timestamp >= start_date
    ).group_by(
        Product.category
    ).order_by(
        desc('revenue')
    ).all()

    if not results:
        return []

    # Calculate total revenue for percentages
    total_revenue = sum(float(row.revenue) for row in results)

    return [
        CategoryBreakdownResponse(
            category=row.category,
            revenue=float(row.revenue),
            revenue_percentage=round((float(row.revenue) / total_revenue * 100), 2) if total_revenue > 0 else 0,
            quantity=int(row.quantity),
            unique_products=int(row.unique_products),
            transaction_count=int(row.transaction_count)
        )
        for row in results
    ]
```

**SQL Executed:**
```sql
SELECT
  products.category,
  SUM(sales.total) AS revenue,
  SUM(sales.quantity) AS quantity,
  COUNT(DISTINCT sales.sku) AS unique_products,
  COUNT(sales.sale_id) AS transaction_count
FROM sales
JOIN products ON sales.sku = products.sku
WHERE sales.timestamp >= '2024-12-17'
GROUP BY products.category
ORDER BY revenue DESC;
```

**6. FRONTEND DISPLAY** (`AnalyticsDashboard.jsx:81`)

```javascript
{!loading && summary && (
  <>
    {/* Summary Cards */}
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <Card className="p-6">
        <div className="text-sm text-gray-600 mb-1">Total Revenue</div>
        <div className="text-3xl font-bold text-green-600">
          {formatCurrency(summary.total_revenue)}
        </div>
        <div className="text-xs text-gray-500 mt-1">
          Avg: {formatCurrency(summary.avg_daily_revenue)}/day
        </div>
      </Card>

      <Card className="p-6">
        <div className="text-sm text-gray-600 mb-1">Units Sold</div>
        <div className="text-3xl font-bold text-blue-600">
          {summary.total_units_sold}
        </div>
        <div className="text-xs text-gray-500 mt-1">
          {summary.unique_products_sold} unique products
        </div>
      </Card>

      <Card className="p-6">
        <div className="text-sm text-gray-600 mb-1">Transactions</div>
        <div className="text-3xl font-bold text-purple-600">
          {summary.total_transactions}
        </div>
        <div className="text-xs text-gray-500 mt-1">
          Avg Order: {formatCurrency(summary.avg_order_value)}
        </div>
      </Card>

      <Card className="p-6">
        <div className="text-sm text-gray-600 mb-1">Best Seller</div>
        <div className="text-lg font-bold text-orange-600">
          {summary.best_selling_product?.name || 'N/A'}
        </div>
        <div className="text-xs text-gray-500 mt-1">
          {summary.best_selling_product?.quantity || 0} units sold
        </div>
      </Card>
    </div>

    {/* Top Products Table */}
    <Card className="p-6 mb-6">
      <h2 className="text-xl font-semibold mb-4">Top 10 Products by Revenue</h2>
      <table className="min-w-full">
        <thead>
          <tr className="border-b">
            <th className="text-left py-2 px-4">Rank</th>
            <th className="text-left py-2 px-4">SKU</th>
            <th className="text-left py-2 px-4">Product Name</th>
            <th className="text-left py-2 px-4">Category</th>
            <th className="text-right py-2 px-4">Revenue</th>
            <th className="text-right py-2 px-4">Quantity</th>
            <th className="text-right py-2 px-4">Transactions</th>
          </tr>
        </thead>
        <tbody>
          {topProducts.map((product, idx) => (
            <tr key={product.sku} className="border-b hover:bg-gray-50">
              <td className="py-2 px-4 font-semibold">{idx + 1}</td>
              <td className="py-2 px-4 font-mono text-sm">{product.sku}</td>
              <td className="py-2 px-4">{product.name}</td>
              <td className="py-2 px-4">
                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                  {product.category}
                </span>
              </td>
              <td className="py-2 px-4 text-right font-semibold">
                {formatCurrency(product.total_revenue)}
              </td>
              <td className="py-2 px-4 text-right">{product.total_quantity}</td>
              <td className="py-2 px-4 text-right">{product.transaction_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>

    {/* Category Breakdown */}
    <Card className="p-6">
      <h2 className="text-xl font-semibold mb-4">Sales by Category</h2>
      <div className="space-y-4">
        {categoryBreakdown.map((category) => (
          <div key={category.category} className="border-b pb-4 last:border-b-0">
            <div className="flex justify-between items-center mb-2">
              <div>
                <span className="font-semibold text-lg">{category.category}</span>
                <span className="text-sm text-gray-500 ml-2">
                  ({category.unique_products} products, {category.transaction_count} transactions)
                </span>
              </div>
              <div className="text-right">
                <div className="font-bold text-lg">{formatCurrency(category.revenue)}</div>
                <div className="text-sm text-gray-600">{category.revenue_percentage}% of total</div>
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-blue-600 h-3 rounded-full transition-all"
                style={{ width: `${category.revenue_percentage}%` }}
              ></div>
            </div>
            <div className="text-sm text-gray-600 mt-1">
              {category.quantity} units sold
            </div>
          </div>
        ))}
      </div>
    </Card>
  </>
)}
```

**7. TIME PERIOD SELECTOR** (`AnalyticsDashboard.jsx:56`)

```javascript
<div className="flex gap-2">
  {[7, 30, 90].map(d => (
    <button
      key={d}
      onClick={() => setDays(d)}
      className={`px-4 py-2 rounded font-medium transition-colors ${
        days === d
          ? 'bg-blue-600 text-white'
          : 'bg-gray-200 hover:bg-gray-300'
      }`}
    >
      {d} Days
    </button>
  ))}
</div>
```

When user clicks a different time period, the `days` state changes, triggering the `useEffect` to re-fetch all analytics data.

### Complete Flow Diagram:

```
USER NAVIGATES TO /analytics
   └─> AnalyticsDashboard component mounts

1. COMPONENT MOUNT (Line 13)
   └─> useState(30) - default 30 days
   └─> useEffect triggers fetchAnalytics()

2. FETCH ANALYTICS (Line 17)
   └─> Make 3 parallel API calls:
       ├─> GET /summary?days=30
       ├─> GET /top-products?days=30&limit=10&sort_by=revenue
       └─> GET /category-breakdown?days=30

3. SUMMARY API (analytics.py Line 280)
   └─> Calculate start_date (30 days ago)
   └─> Query: SELECT * FROM sales WHERE timestamp >= start_date
   └─> Calculate metrics:
       ├─> total_revenue = SUM(total)
       ├─> total_units = SUM(quantity)
       ├─> total_transactions = COUNT(*)
       ├─> unique_products = COUNT(DISTINCT sku)
       ├─> avg_order_value = revenue / transactions
       ├─> avg_daily_revenue = revenue / days
       └─> Find best_selling_product (max quantity)
   └─> Return summary dict

4. TOP PRODUCTS API (analytics.py Line 20)
   └─> Query with JOIN:
       SELECT sku, name, category,
              SUM(total) as revenue,
              SUM(quantity) as quantity,
              COUNT(*) as transactions
       FROM sales JOIN products
       WHERE timestamp >= start_date
       GROUP BY sku, name, category
       ORDER BY revenue DESC
       LIMIT 10
   └─> Return List[TopProductResponse]

5. CATEGORY BREAKDOWN API (analytics.py Line 102)
   └─> Query with JOIN:
       SELECT category,
              SUM(total) as revenue,
              SUM(quantity) as quantity,
              COUNT(DISTINCT sku) as unique_products,
              COUNT(*) as transactions
       FROM sales JOIN products
       WHERE timestamp >= start_date
       GROUP BY category
       ORDER BY revenue DESC
   └─> Calculate revenue_percentage for each category
   └─> Return List[CategoryBreakdownResponse]

6. FRONTEND UPDATE (Line 24, 31, 36)
   └─> setSummary(summaryRes.data)
   └─> setTopProducts(topProductsRes.data)
   └─> setCategoryBreakdown(categoryRes.data)
   └─> Component re-renders

7. DISPLAY (Line 81)
   └─> Render 4 summary cards:
       ├─> Total Revenue (with avg daily)
       ├─> Units Sold (with unique products)
       ├─> Transactions (with avg order value)
       └─> Best Seller (with quantity)
   └─> Render Top 10 Products table
   └─> Render Category Breakdown with progress bars

8. USER CHANGES TIME PERIOD (Line 62)
   └─> Click "7 Days" or "90 Days" button
   └─> setDays(7) or setDays(90)
   └─> useEffect triggers (depends on [days])
   └─> fetchAnalytics() runs again with new days value
   └─> All data refreshes

USER SEES:
   └─> Real-time business intelligence dashboard
   └─> Key performance indicators (KPIs)
   └─> Top performing products
   └─> Category performance breakdown
   └─> Visual progress bars showing category contribution
   └─> Ability to switch time periods (7/30/90 days)
```

---

## 7.2 ABC Analysis Algorithm

**File**: `backend/app/api/v1/analytics.py:200`

ABC Analysis is an inventory categorization technique that divides products into three categories based on their revenue contribution:
- **A**: Top 80% of revenue (typically ~20% of products) - Most important
- **B**: Next 15% of revenue (typically ~30% of products) - Moderately important
- **C**: Remaining 5% of revenue (typically ~50% of products) - Least important

This follows the **Pareto Principle** (80/20 rule).

### Algorithm Implementation:

```python
@router.get("/abc-analysis", response_model=List[ABCAnalysisResponse])
async def get_abc_analysis(
    days: int = Query(90, ge=30, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
) -> List[ABCAnalysisResponse]:

    # STEP 1: Calculate date range
    start_date = datetime.utcnow() - timedelta(days=days)

    # STEP 2: Query product revenue (sorted descending)
    product_revenue = db.query(
        Sale.sku,
        Product.name,
        Product.category,
        func.sum(Sale.total).label('revenue'),
        func.sum(Sale.quantity).label('quantity')
    ).join(
        Product, Sale.sku == Product.sku
    ).filter(
        Sale.timestamp >= start_date
    ).group_by(
        Sale.sku,
        Product.name,
        Product.category
    ).order_by(
        desc('revenue')  # CRITICAL: Sort by revenue descending
    ).all()

    if not product_revenue:
        return []

    # STEP 3: Calculate total revenue
    total_revenue = sum(float(row.revenue) for row in product_revenue)

    # STEP 4: Calculate cumulative percentages and classify
    results = []
    cumulative_revenue = 0

    for row in product_revenue:
        revenue = float(row.revenue)
        cumulative_revenue += revenue

        # Calculate percentages
        cumulative_percentage = (cumulative_revenue / total_revenue * 100) if total_revenue > 0 else 0
        revenue_percentage = (revenue / total_revenue * 100) if total_revenue > 0 else 0

        # STEP 5: Classify into A, B, or C
        if cumulative_percentage <= 80:
            classification = "A"  # Top 80% of revenue
        elif cumulative_percentage <= 95:
            classification = "B"  # Next 15% of revenue
        else:
            classification = "C"  # Remaining 5% of revenue

        results.append(
            ABCAnalysisResponse(
                sku=row.sku,
                name=row.name,
                category=row.category,
                revenue=revenue,
                quantity=int(row.quantity),
                revenue_percentage=round(revenue_percentage, 2),
                cumulative_revenue_percentage=round(cumulative_percentage, 2),
                abc_classification=classification
            )
        )

    return results
```

### Example Calculation:

**Given 10 products sorted by revenue:**

| Rank | SKU | Revenue | % of Total | Cumulative % | Classification |
|------|-----|---------|------------|--------------|----------------|
| 1 | SAR001 | ₹50,000 | 33.3% | 33.3% | A |
| 2 | KUR002 | ₹40,000 | 26.7% | 60.0% | A |
| 3 | LEH003 | ₹30,000 | 20.0% | 80.0% | A (last one) |
| 4 | DUP004 | ₹10,000 | 6.7% | 86.7% | B |
| 5 | SAL005 | ₹8,000 | 5.3% | 92.0% | B |
| 6 | BLO006 | ₹4,500 | 3.0% | 95.0% | B (last one) |
| 7 | TOP007 | ₹3,000 | 2.0% | 97.0% | C |
| 8 | SKI008 | ₹2,000 | 1.3% | 98.3% | C |
| 9 | PAN009 | ₹1,500 | 1.0% | 99.3% | C |
| 10 | DRE010 | ₹1,000 | 0.7% | 100.0% | C |

**Total Revenue**: ₹1,50,000

**Results:**
- **Category A** (3 products, 30%): ₹1,20,000 revenue (80%)
- **Category B** (3 products, 30%): ₹22,500 revenue (15%)
- **Category C** (4 products, 40%): ₹7,500 revenue (5%)

### Business Implications:

**Category A Products:**
- Focus maximum attention
- Tight inventory control
- Frequent monitoring
- Never stock out
- Premium placement in store

**Category B Products:**
- Moderate attention
- Standard inventory control
- Regular monitoring
- Maintain adequate stock

**Category C Products:**
- Minimal attention
- Loose inventory control
- Periodic review
- Order as needed
- May stock out occasionally

---

# 8.0 Import Relationships

This section documents how files are imported and connected throughout the application, showing the dependency graph.

## 8.1 Frontend Import Map

### Core Infrastructure

**`frontend/src/main.jsx`** (Entry Point)
```javascript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

**`frontend/src/App.jsx`** (Root Component)
```javascript
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Auth/Login'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import ProductList from './pages/Products/ProductList'
import ProductForm from './pages/Products/ProductForm'
import SalesHistory from './pages/Sales/SalesHistory'
import InventoryDashboard from './pages/Inventory/InventoryDashboard'
import ForecastDashboard from './pages/Forecasting/ForecastDashboard'
import AnalyticsDashboard from './pages/Analytics/AnalyticsDashboard'
import ProtectedRoute from './components/auth/ProtectedRoute'

// Routes definition connecting all pages
```

### API Client (Critical Dependency)

**`frontend/src/api/client.js`**
```javascript
import axios from 'axios'

// Used by ALL page components for API calls
// Imported as: import api from '../../api/client'
```

**Files that import client.js:**
- `pages/Auth/Login.jsx` → Authentication
- `pages/Dashboard.jsx` → Dashboard data
- `pages/Products/ProductList.jsx` → Product listing
- `pages/Products/ProductForm.jsx` → Product CRUD
- `pages/Sales/SalesHistory.jsx` → Sales data
- `pages/Inventory/InventoryDashboard.jsx` → Inventory data
- `pages/Forecasting/ForecastDashboard.jsx` → Forecast data
- `pages/Analytics/AnalyticsDashboard.jsx` → Analytics data

### Common Components (Reused Across Pages)

**`frontend/src/components/common/Card.jsx`**
```javascript
// Pure presentation component
// No imports except React
```

**Used by:**
- Dashboard.jsx
- ProductList.jsx
- SalesHistory.jsx
- InventoryDashboard.jsx
- ForecastDashboard.jsx
- AnalyticsDashboard.jsx

**`frontend/src/components/common/Button.jsx`**
```javascript
// Pure presentation component
```

**Used by:**
- ProductForm.jsx
- SalesHistory.jsx
- ForecastDashboard.jsx

### Layout Components

**`frontend/src/components/layout/Layout.jsx`**
```javascript
import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'
import Sidebar from './Sidebar'

// Wraps all protected routes
```

**`frontend/src/components/layout/Navbar.jsx`**
```javascript
import { useNavigate } from 'react-router-dom'

// Handles logout → removes token → redirects to /login
```

**`frontend/src/components/layout/Sidebar.jsx`**
```javascript
import { Link, useLocation } from 'react-router-dom'

// Navigation menu with active state highlighting
```

### Frontend Dependency Graph:

```
main.jsx
  └─> App.jsx
      ├─> react-router-dom (BrowserRouter, Routes, Route)
      ├─> Login.jsx
      │   └─> api/client.js
      │       └─> axios
      │
      └─> ProtectedRoute
          └─> Layout.jsx
              ├─> Navbar.jsx
              │   └─> react-router-dom (useNavigate)
              │
              ├─> Sidebar.jsx
              │   └─> react-router-dom (Link, useLocation)
              │
              └─> Outlet (renders child routes)
                  ├─> Dashboard.jsx
                  │   ├─> api/client.js
                  │   ├─> Card.jsx
                  │   └─> recharts (for charts)
                  │
                  ├─> ProductList.jsx
                  │   ├─> api/client.js
                  │   └─> Card.jsx
                  │
                  ├─> ProductForm.jsx
                  │   ├─> api/client.js
                  │   └─> Button.jsx
                  │
                  ├─> SalesHistory.jsx
                  │   ├─> api/client.js
                  │   ├─> Card.jsx
                  │   └─> Button.jsx
                  │
                  ├─> InventoryDashboard.jsx
                  │   ├─> api/client.js
                  │   └─> Card.jsx
                  │
                  ├─> ForecastDashboard.jsx
                  │   ├─> api/client.js
                  │   ├─> Card.jsx
                  │   ├─> Button.jsx
                  │   └─> ForecastChart.jsx
                  │       └─> recharts
                  │
                  └─> AnalyticsDashboard.jsx
                      ├─> api/client.js
                      └─> Card.jsx
```

**Key Observation:**
- **api/client.js** is the MOST CRITICAL import - used by every page that fetches data
- React Router hooks (useNavigate, useLocation, Link) used throughout for navigation
- Common components (Card, Button) reduce code duplication

---

## 8.2 Backend Import Map

### Application Entry Point

**`backend/main.py`** (FastAPI Application)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, products, sales, inventory, analytics, forecasting
from app.database import engine, Base

app = FastAPI(title="Garb & Glitz Inventory API")

# Include all routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(products.router, prefix="/api/v1", tags=["products"])
app.include_router(sales.router, prefix="/api/v1", tags=["sales"])
app.include_router(inventory.router, prefix="/api/v1", tags=["inventory"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
app.include_router(forecasting.router, prefix="/api/v1", tags=["forecasting"])
```

### API Routes Layer

**Each route file follows this pattern:**

**`backend/app/api/v1/products.py`**
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db  # Database session
from app.models.products import Product  # SQLAlchemy model
from app.models.suppliers import Supplier  # Related model
from app.schemas.products import ProductCreate, ProductResponse  # Pydantic schemas

router = APIRouter()

# Route functions use: get_db, Product, ProductCreate, ProductResponse
```

**`backend/app/api/v1/sales.py`**
```python
from app.dependencies import get_db
from app.models.sales import Sale
from app.models.products import Product
from app.models.inventory import InventoryLedger
from app.schemas.sales import SaleCreate, SaleResponse

# Uses multiple models: Sale, Product, InventoryLedger
```

**`backend/app/api/v1/analytics.py`**
```python
from app.dependencies import get_db
from app.models.sales import Sale
from app.models.products import Product
from app.schemas.analytics import TopProductResponse, CategoryBreakdownResponse, ABCAnalysisResponse
from sqlalchemy import func, desc  # SQL aggregation functions

# Heavy use of SQLAlchemy aggregations
```

**`backend/app/api/v1/forecasting.py`**
```python
from app.dependencies import get_db
from app.models.sales import Sale
from app.models.products import Product
from app.schemas import ForecastResponse, ForecastDataPoint
import numpy as np  # For statistical calculations

# Uses numpy for exponential smoothing algorithm
```

### Database Layer

**`backend/app/database.py`**
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Database connection configuration
# Imported by: dependencies.py, main.py
```

**`backend/app/dependencies.py`**
```python
from sqlalchemy.orm import Session
from app.database import SessionLocal

def get_db():
    # Database session dependency
    # Injected into EVERY route function via Depends(get_db)
```

### Models Layer

**`backend/app/models/users.py`**
```python
from sqlalchemy import Column, String, Boolean, DateTime
from app.database import Base

# Used by: api/v1/auth.py
```

**`backend/app/models/products.py`**
```python
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

# Used by: api/v1/products.py, sales.py, analytics.py, forecasting.py
```

**`backend/app/models/sales.py`**
```python
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base

# Used by: api/v1/sales.py, analytics.py, forecasting.py
```

**`backend/app/models/inventory.py`**
```python
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base

# Used by: api/v1/sales.py, inventory.py
```

### Schemas Layer (Pydantic)

**`backend/app/schemas/products.py`**
```python
from pydantic import BaseModel, Field
from typing import Optional

# ProductCreate - Input validation for POST /products
# ProductResponse - Output serialization for GET /products
```

**`backend/app/schemas/sales.py`**
```python
from pydantic import BaseModel, Field
from datetime import datetime

# SaleCreate - Input validation for POST /sales
# SaleResponse - Output serialization for GET /sales
```

**`backend/app/schemas/analytics.py`**
```python
from pydantic import BaseModel
from typing import List

# TopProductResponse, CategoryBreakdownResponse, ABCAnalysisResponse
```

### Authentication Layer

**`backend/app/auth.py`**
```python
from passlib.context import CryptContext  # Password hashing
from jose import jwt  # JWT token creation/verification
from app.config import settings
from app.models.users import User

# Used by: api/v1/auth.py (login, token creation)
# Used by: ALL protected routes via get_current_user dependency
```

### Backend Dependency Graph:

```
main.py
  ├─> FastAPI
  ├─> CORSMiddleware
  ├─> database.py
  │   ├─> SQLAlchemy (create_engine, sessionmaker)
  │   └─> config.py (DATABASE_URL)
  │
  └─> API Routers:
      ├─> api/v1/auth.py
      │   ├─> dependencies.py (get_db)
      │   ├─> models/users.py
      │   ├─> schemas/auth.py
      │   └─> auth.py (authenticate_user, create_access_token)
      │       ├─> passlib (bcrypt hashing)
      │       ├─> jose (JWT)
      │       └─> config.py (SECRET_KEY, ALGORITHM)
      │
      ├─> api/v1/products.py
      │   ├─> dependencies.py (get_db)
      │   ├─> models/products.py
      │   ├─> models/suppliers.py
      │   └─> schemas/products.py
      │
      ├─> api/v1/sales.py
      │   ├─> dependencies.py (get_db)
      │   ├─> models/sales.py
      │   ├─> models/products.py
      │   ├─> models/inventory.py (InventoryLedger)
      │   └─> schemas/sales.py
      │
      ├─> api/v1/inventory.py
      │   ├─> dependencies.py (get_db)
      │   ├─> models/inventory.py
      │   ├─> models/products.py
      │   └─> schemas/inventory.py
      │
      ├─> api/v1/analytics.py
      │   ├─> dependencies.py (get_db)
      │   ├─> models/sales.py
      │   ├─> models/products.py
      │   ├─> schemas/analytics.py
      │   └─> SQLAlchemy (func, desc) - for aggregations
      │
      └─> api/v1/forecasting.py
          ├─> dependencies.py (get_db)
          ├─> models/sales.py
          ├─> models/products.py
          ├─> schemas/forecasting.py
          └─> numpy - for exponential smoothing algorithm
```

**Key Observations:**

1. **dependencies.py (get_db)** is imported by EVERY route file
2. **models/products.py** and **models/sales.py** are the most frequently imported models
3. **SQLAlchemy** is used throughout for database operations
4. **Pydantic schemas** provide automatic request/response validation
5. **auth.py** provides authentication utilities used across the application

---

## 8.3 Critical Import Paths

### Authentication Flow Imports:

```
Frontend: Login.jsx
  └─> import api from '../../api/client'
      └─> import axios

Backend: api/v1/auth.py
  └─> from app.auth import authenticate_user, create_access_token
      ├─> from passlib.context import CryptContext
      ├─> from jose import jwt
      └─> from app.models.users import User
          └─> from app.database import Base
```

### Product Creation Flow Imports:

```
Frontend: ProductForm.jsx
  └─> import api from '../../api/client'
      └─> import axios

Backend: api/v1/products.py
  ├─> from app.dependencies import get_db
  │   └─> from app.database import SessionLocal
  ├─> from app.models.products import Product
  │   └─> from app.database import Base
  ├─> from app.models.suppliers import Supplier
  └─> from app.schemas.products import ProductCreate, ProductResponse
      └─> from pydantic import BaseModel, Field
```

### Sales Creation Flow Imports:

```
Backend: api/v1/sales.py
  ├─> from app.dependencies import get_db
  ├─> from app.models.sales import Sale
  │   └─> from app.database import Base
  ├─> from app.models.products import Product
  ├─> from app.models.inventory import InventoryLedger
  │   └─> from app.database import Base
  └─> from app.schemas.sales import SaleCreate, SaleResponse
```

### Forecasting Flow Imports:

```
Frontend: ForecastDashboard.jsx
  ├─> import api from '../../api/client'
  ├─> import Card from '../../components/common/Card'
  ├─> import Button from '../../components/common/Button'
  └─> import ForecastChart from './ForecastChart'
      └─> import { LineChart, Line, XAxis, YAxis } from 'recharts'

Backend: api/v1/forecasting.py
  ├─> from app.dependencies import get_db
  ├─> from app.models.sales import Sale
  ├─> from app.models.products import Product
  ├─> from app.schemas import ForecastResponse, ForecastDataPoint
  ├─> import numpy as np  # CRITICAL for algorithm
  └─> from datetime import datetime, timedelta
```

---

# 9.0 Data Structures & Algorithms

This section documents all DSA implementations in the codebase.

## 9.1 Exponential Smoothing Algorithm

**Location**: `backend/app/api/v1/forecasting.py:18`

**Algorithm Type**: Time Series Forecasting

**Data Structures Used:**
- **List**: `sales_data` (historical time series)
- **List**: `quantities` (extracted values)
- **List**: `forecast` (output predictions)
- **NumPy Array** (internally in np.mean, np.std, np.sqrt)

**Time Complexity**: O(n + h)
- n = number of historical data points
- h = forecast horizon days

**Space Complexity**: O(n + h)
- Stores historical data and forecast results

**Algorithm:**
```python
def calculate_forecast(sales_data: list, horizon_days: int) -> list[ForecastDataPoint]:
    # 1. Extract quantities - O(n)
    quantities = [qty for _, qty in sales_data]

    # 2. Calculate statistics - O(n)
    baseline = np.mean(quantities)  # Average
    std_dev = np.std(quantities)    # Standard deviation

    # 3. Initialize - O(1)
    alpha = 0.3  # Smoothing parameter
    smoothed_value = quantities[-1]

    # 4. Generate forecast - O(h)
    forecast = []
    for day in range(1, horizon_days + 1):
        # Calculate trend - O(1)
        trend = (quantities[-1] - quantities[0]) / len(quantities)

        # Apply exponential smoothing - O(1)
        smoothed_value = alpha * last_value + (1 - alpha) * (smoothed_value + trend)

        # Calculate confidence intervals - O(1)
        margin = 1.96 * std_dev * np.sqrt(day)

        # Append forecast point - O(1)
        forecast.append(ForecastDataPoint(
            date=forecast_date,
            value=smoothed_value,
            lower_bound=smoothed_value - margin,
            upper_bound=smoothed_value + margin
        ))

    return forecast  # O(h) list
```

**Mathematical Formulas:**

1. **Exponential Smoothing:**
   ```
   S_t = α * X_t + (1 - α) * (S_t-1 + T)
   ```

2. **Trend:**
   ```
   T = (X_last - X_first) / n
   ```

3. **Confidence Interval:**
   ```
   CI = ±1.96 * σ * √h
   ```

---

## 9.2 ABC Analysis Algorithm

**Location**: `backend/app/api/v1/analytics.py:200`

**Algorithm Type**: Inventory Categorization (Pareto Principle)

**Data Structures Used:**
- **List**: `product_revenue` (sorted by revenue)
- **Dictionary** (implicit in row objects)
- **List**: `results` (classified products)

**Time Complexity**: O(n log n + n)
- O(n log n): SQL ORDER BY revenue DESC (database sort)
- O(n): Single pass through sorted data

**Space Complexity**: O(n)
- Stores all products with classifications

**Algorithm:**
```python
def get_abc_analysis(days: int, db: Session) -> List[ABCAnalysisResponse]:
    # 1. Query and sort by revenue - O(n log n) in database
    product_revenue = db.query(
        Sale.sku,
        func.sum(Sale.total).label('revenue'),
        func.sum(Sale.quantity).label('quantity')
    ).group_by(Sale.sku)\
     .order_by(desc('revenue'))\  # CRITICAL: Sort descending
     .all()

    # 2. Calculate total - O(n)
    total_revenue = sum(float(row.revenue) for row in product_revenue)

    # 3. Single pass classification - O(n)
    cumulative_revenue = 0
    results = []

    for row in product_revenue:  # Already sorted!
        revenue = float(row.revenue)
        cumulative_revenue += revenue

        # Calculate cumulative percentage
        cumulative_percentage = (cumulative_revenue / total_revenue * 100)

        # Classify based on cumulative percentage
        if cumulative_percentage <= 80:
            classification = "A"   # Top 80% of revenue
        elif cumulative_percentage <= 95:
            classification = "B"   # Next 15% of revenue
        else:
            classification = "C"   # Remaining 5% of revenue

        results.append(ABCAnalysisResponse(
            sku=row.sku,
            revenue=revenue,
            cumulative_revenue_percentage=cumulative_percentage,
            abc_classification=classification
        ))

    return results
```

**Why This Works:**
- Products are sorted by revenue descending
- Single pass calculates cumulative percentage
- Classification thresholds (80%, 95%) applied in real-time
- No need for multiple passes or complex data structures

**Pareto Principle:**
- ~20% of products → 80% of revenue (Category A)
- ~30% of products → 15% of revenue (Category B)
- ~50% of products → 5% of revenue (Category C)

---

## 9.3 Inventory Ledger System

**Location**: `backend/app/models/inventory.py`, used in `backend/app/api/v1/sales.py`

**Data Structure**: Append-Only Log (Event Sourcing Pattern)

**Schema:**
```python
class InventoryLedger(Base):
    __tablename__ = "inventory_ledger"

    ledger_id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String(50), nullable=False)
    change_qty = Column(Integer, nullable=False)   # +/- quantity
    balance_qty = Column(Integer, nullable=False)  # Running total
    reason = Column(String(255))                    # Traceability
    timestamp = Column(DateTime, default=datetime.utcnow)
```

**Algorithm**: Running Balance Calculation

**Time Complexity**: O(n)
- n = number of ledger entries for a SKU

**Current Stock Query:**
```python
current_stock = db.query(func.sum(InventoryLedger.change_qty))\
    .filter(InventoryLedger.sku == sku)\
    .scalar() or 0
```

**SQL:**
```sql
SELECT SUM(change_qty) FROM inventory_ledger WHERE sku = 'SAR001';
```

**Example Ledger Entries:**

| ledger_id | sku | change_qty | balance_qty | reason | timestamp |
|-----------|-----|------------|-------------|---------|-----------|
| 1 | SAR001 | +100 | 100 | Purchase PO-001 | 2025-01-01 |
| 2 | SAR001 | -5 | 95 | Sale INV-001 | 2025-01-05 |
| 3 | SAR001 | -8 | 87 | Sale INV-002 | 2025-01-07 |
| 4 | SAR001 | +50 | 137 | Purchase PO-002 | 2025-01-10 |
| 5 | SAR001 | -3 | 134 | Sale INV-003 | 2025-01-12 |

**Current Stock**: SUM(100, -5, -8, +50, -3) = 134

**Benefits:**
- Full audit trail
- Can reconstruct stock at any point in time
- Immutable records (append-only)
- Transaction traceability

---

## 9.4 Aggregation Algorithms (Analytics)

### Top Products by Revenue

**Location**: `backend/app/api/v1/analytics.py:20`

**Algorithm**: SQL GROUP BY with SUM aggregation

**SQL:**
```sql
SELECT
  sku,
  SUM(total) AS total_revenue,
  SUM(quantity) AS total_quantity,
  COUNT(*) AS transaction_count
FROM sales
WHERE timestamp >= '2024-12-17'
GROUP BY sku
ORDER BY total_revenue DESC
LIMIT 10;
```

**Time Complexity**: O(n log n)
- n = number of sales records
- Dominated by sort (ORDER BY)

**Space Complexity**: O(k)
- k = number of unique SKUs
- Only stores aggregated results

### Category Breakdown

**Location**: `backend/app/api/v1/analytics.py:102`

**Algorithm**: SQL GROUP BY with JOIN

**SQL:**
```sql
SELECT
  products.category,
  SUM(sales.total) AS revenue,
  SUM(sales.quantity) AS quantity,
  COUNT(DISTINCT sales.sku) AS unique_products
FROM sales
JOIN products ON sales.sku = products.sku
WHERE sales.timestamp >= '2024-12-17'
GROUP BY products.category
ORDER BY revenue DESC;
```

**Time Complexity**: O(n + m + k log k)
- n = sales records
- m = products records
- k = number of categories
- JOIN + GROUP BY + SORT

**Post-Processing** (Calculate Percentages):
```python
total_revenue = sum(row.revenue for row in results)  # O(k)

for row in results:  # O(k)
    revenue_percentage = (row.revenue / total_revenue * 100)
```

**Total Complexity**: O(n + m + k log k + k) = O(n + m + k log k)

---

## 9.5 Data Structure Summary

| Data Structure | Usage | Location |
|----------------|-------|----------|
| **List** | Historical sales data, forecast results | forecasting.py |
| **Dictionary** | Product sales aggregation, SKU mapping | analytics.py (Python dict), auth.py |
| **NumPy Array** | Statistical calculations (mean, std, sqrt) | forecasting.py |
| **SQLAlchemy ORM** | Database models (Products, Sales, Users) | models/*.py |
| **Pydantic Models** | Request/Response validation | schemas/*.py |
| **Hash Table** | localStorage (JWT tokens) | Frontend |
| **Queue** | Event queue (React state updates) | Frontend (React) |
| **Tree** | React component tree, DOM | Frontend |

### Database Indexes:

**Implicit Indexes** (Primary Keys):
- `products.sku` (Primary Key) → B-Tree index
- `sales.sale_id` (Primary Key) → B-Tree index
- `users.username` (Unique) → B-Tree index

**Query Optimization:**
All queries benefit from these indexes, especially:
- `WHERE sku = 'SAR001'` → Index seek (O(log n))
- `JOIN products ON sales.sku = products.sku` → Index join

---

