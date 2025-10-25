# Inventory Management System

A full-stack inventory management system built with FastAPI, React, PostgreSQL, and Redis. Features real-time inventory tracking, demand forecasting, supplier management, and comprehensive reporting.

## Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- PostgreSQL 15 - Primary database
- Redis 7 - Caching and session management
- SQLAlchemy - ORM
- Alembic - Database migrations
- Prophet - Demand forecasting

**Frontend:**
- React 18 - UI framework
- Vite - Build tool
- TailwindCSS - Styling
- React Router - Navigation
- Axios - HTTP client

**DevOps:**
- Docker & Docker Compose - Containerization
- Nginx - Reverse proxy and static file serving
- GitHub Actions - CI/CD (optional)

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- Git

## Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd inventory-management-system
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration (optional for development)
```

3. **Start the services**
```bash
docker-compose up -d
```

4. **Seed the database with sample data**
```bash
chmod +x scripts/seed_db.sh
./scripts/seed_db.sh
```

5. **Access the application**
- Frontend: http://localhost:3000
- API Documentation: http://localhost:8000/docs
- API Redoc: http://localhost:8000/redoc

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ HTTP :3000
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + Nginx)                  │
│  - SPA Routing                                               │
│  - Static Assets                                             │
│  - API Proxy (/api → backend:8000)                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ HTTP :8000
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  - REST API                                                  │
│  - Business Logic                                            │
│  - Authentication/Authorization                              │
└───────────┬─────────────────────┬───────────────────────────┘
            │                     │
            │ :5432               │ :6379
            ▼                     ▼
┌───────────────────┐   ┌──────────────────┐
│  PostgreSQL 15    │   │    Redis 7       │
│  - Main Database  │   │  - Cache         │
│  - Persistent     │   │  - Sessions      │
└───────────────────┘   └──────────────────┘
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - User logout

### Products
- `GET /api/products` - List all products
- `GET /api/products/{id}` - Get product details
- `POST /api/products` - Create new product
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product
- `GET /api/products/low-stock` - Get low stock items

### Categories
- `GET /api/categories` - List all categories
- `POST /api/categories` - Create category
- `PUT /api/categories/{id}` - Update category
- `DELETE /api/categories/{id}` - Delete category

### Suppliers
- `GET /api/suppliers` - List all suppliers
- `POST /api/suppliers` - Create supplier
- `PUT /api/suppliers/{id}` - Update supplier
- `DELETE /api/suppliers/{id}` - Delete supplier

### Inventory
- `POST /api/inventory/adjust` - Adjust inventory levels
- `GET /api/inventory/transactions` - Get transaction history
- `GET /api/inventory/forecast` - Demand forecasting

### Reports
- `GET /api/reports/inventory-summary` - Inventory summary
- `GET /api/reports/sales` - Sales report
- `GET /api/reports/low-stock` - Low stock report
- `GET /api/reports/export` - Export reports (CSV/Excel)

## Development

### Backend Development

```bash
# Access backend container
docker-compose exec backend bash

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Run tests
pytest

# View logs
docker-compose logs -f backend
```

### Frontend Development

```bash
# Access frontend container
docker-compose exec frontend sh

# Install new package (requires rebuild)
npm install <package-name>

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend

# View logs
docker-compose logs -f frontend
```

### Database Management

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U inventory -d inventory_db

# Create backup
chmod +x scripts/backup_db.sh
./scripts/backup_db.sh

# Restore from backup
docker-compose exec -T postgres psql -U inventory -d inventory_db < backups/backup_YYYYMMDD_HHMMSS.sql

# Reset database
docker-compose down -v
docker-compose up -d
./scripts/seed_db.sh
```

## Environment Variables

Key environment variables (see `.env.example` for full list):

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT secret key (change in production!)
- `ENVIRONMENT` - development/staging/production
- `VITE_API_URL` - API base URL for frontend

## Production Deployment

### Security Checklist
- [ ] Change all default passwords
- [ ] Generate strong `SECRET_KEY`
- [ ] Set `ENVIRONMENT=production`
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up automated backups
- [ ] Configure monitoring and alerts
- [ ] Review CORS settings
- [ ] Enable rate limiting
- [ ] Set up log aggregation

### Deployment Steps

1. **Update environment variables for production**
```bash
cp .env.example .env.production
# Edit .env.production with production values
```

2. **Build and start services**
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

3. **Run migrations**
```bash
docker-compose exec backend alembic upgrade head
```

4. **Set up automated backups (cron job)**
```bash
# Add to crontab - runs daily at 2 AM
0 2 * * * /path/to/scripts/backup_db.sh >> /var/log/backup.log 2>&1
```

5. **Configure Nginx SSL (recommended)**
```bash
# Install certbot for Let's Encrypt
sudo apt-get install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com
```

### Monitoring

```bash
# View all service status
docker-compose ps

# Monitor resource usage
docker stats

# View logs
docker-compose logs -f

# Check specific service logs
docker-compose logs -f backend
docker-compose logs -f postgres
```

### Scaling

To scale backend services:
```bash
docker-compose up -d --scale backend=3
```

Add load balancer configuration in `docker-compose.prod.yml`.

## Troubleshooting

### Common Issues

**Issue: Backend won't start**
```bash
# Check logs
docker-compose logs backend

# Verify database connection
docker-compose exec postgres pg_isready -U inventory

# Restart services
docker-compose restart backend
```

**Issue: Frontend can't connect to API**
- Check `VITE_API_URL` in `.env`
- Verify backend is running: `curl http://localhost:8000/health`
- Check browser console for CORS errors

**Issue: Database connection failed**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U inventory -d inventory_db -c "SELECT 1;"

# Reset database if corrupted
docker-compose down -v
docker-compose up -d
```

**Issue: Out of disk space**
```bash
# Clean up old Docker images
docker system prune -a

# Remove old backups
find ./backups -name "backup_*.sql*" -mtime +30 -delete
```

## Testing

### Backend Tests
```bash
# Run all tests
docker-compose exec backend pytest

# Run with coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Run specific test file
docker-compose exec backend pytest tests/test_products.py
```

### Frontend Tests
```bash
# Run tests (requires test setup)
docker-compose exec frontend npm test

# Run E2E tests
docker-compose exec frontend npm run test:e2e
```

## Performance Optimization

### Database
- Indexes are automatically created via migrations
- Regular `VACUUM` and `ANALYZE` operations
- Connection pooling configured in SQLAlchemy

### Caching
- Redis caching for frequently accessed data
- API response caching for GET endpoints
- Session management via Redis

### Frontend
- Production build with minification
- Gzip compression enabled in Nginx
- Static asset caching (1 year)
- Code splitting with React lazy loading

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Submit a pull request

### Code Style
- Backend: Follow PEP 8, use `black` for formatting
- Frontend: ESLint + Prettier configuration
- Commit messages: Use conventional commits format

## Backup and Recovery

### Automated Backups
The `backup_db.sh` script creates timestamped backups and handles retention:
```bash
# Manual backup
./scripts/backup_db.sh

# Backups are stored in ./backups/
# Default retention: 30 days
```

### Restore from Backup
```bash
# List available backups
ls -lh backups/

# Restore specific backup
gunzip -c backups/backup_20250124_020000.sql.gz | \
  docker-compose exec -T postgres psql -U inventory -d inventory_db

# Or for uncompressed backups
docker-compose exec -T postgres psql -U inventory -d inventory_db < backups/backup_20250124_020000.sql
```

## License

[Your License Here]

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Email: support@yourcompany.com
- Documentation: [docs-url]

## Acknowledgments

Built with open-source technologies:
- FastAPI - https://fastapi.tiangolo.com/
- React - https://react.dev/
- PostgreSQL - https://www.postgresql.org/
- Redis - https://redis.io/