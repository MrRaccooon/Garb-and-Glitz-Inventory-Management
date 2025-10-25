#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting database seeding process...${NC}"

# Check if Docker Compose is running
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${RED}Error: Docker Compose services are not running${NC}"
    echo "Please start services with: docker-compose up -d"
    exit 1
fi

# Wait for backend to be healthy
echo -e "${YELLOW}Waiting for backend service to be healthy...${NC}"
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker-compose exec -T backend curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}Backend service is healthy${NC}"
        break
    fi
    attempt=$((attempt + 1))
    echo "Attempt $attempt/$max_attempts: Waiting for backend..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}Error: Backend service did not become healthy${NC}"
    exit 1
fi

# Check if database already has data
echo -e "${YELLOW}Checking if database already contains data...${NC}"
product_count=$(docker-compose exec -T postgres psql -U inventory -d inventory_db -t -c "SELECT COUNT(*) FROM products;" 2>/dev/null | tr -d ' ')

if [ -z "$product_count" ]; then
    echo -e "${YELLOW}Products table doesn't exist yet. Running migrations...${NC}"
    docker-compose exec -T backend alembic upgrade head
    product_count=0
fi

if [ "$product_count" -gt 0 ]; then
    echo -e "${YELLOW}Database already contains $product_count products${NC}"
    read -p "Do you want to reseed the database? This will clear existing data (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Clearing existing data...${NC}"
        docker-compose exec -T backend python scripts/seed_db.py --clear
    else
        echo -e "${GREEN}Skipping database seeding${NC}"
        exit 0
    fi
fi

# Run the seed script
echo -e "${YELLOW}Seeding database with sample data...${NC}"
if docker-compose exec -T backend python scripts/seed_db.py; then
    echo -e "${GREEN}✓ Database seeding completed successfully!${NC}"
    
    # Display summary
    echo -e "\n${GREEN}Database Summary:${NC}"
    docker-compose exec -T postgres psql -U inventory -d inventory_db -c "
        SELECT 'Products' as table_name, COUNT(*) as count FROM products
        UNION ALL
        SELECT 'Categories', COUNT(*) FROM categories
        UNION ALL
        SELECT 'Suppliers', COUNT(*) FROM suppliers
        UNION ALL
        SELECT 'Users', COUNT(*) FROM users;
    "
else
    echo -e "${RED}✗ Database seeding failed${NC}"
    exit 1
fi

echo -e "\n${GREEN}You can now access:${NC}"
echo -e "  Frontend: ${YELLOW}http://localhost:3000${NC}"
echo -e "  API Docs: ${YELLOW}http://localhost:8000/docs${NC}"