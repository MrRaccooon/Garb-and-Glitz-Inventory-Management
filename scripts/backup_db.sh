#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${TIMESTAMP}.sql"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_FILE}"
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}

echo -e "${YELLOW}Starting database backup process...${NC}"

# Create backup directory if it doesn't exist
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${YELLOW}Creating backup directory: ${BACKUP_DIR}${NC}"
    mkdir -p "$BACKUP_DIR"
fi

# Check if Docker Compose is running
if ! docker-compose ps | grep -q "postgres.*Up"; then
    echo -e "${RED}Error: PostgreSQL container is not running${NC}"
    echo "Please start services with: docker-compose up -d"
    exit 1
fi

# Create backup
echo -e "${YELLOW}Creating backup: ${BACKUP_FILE}${NC}"
if docker-compose exec -T postgres pg_dump -U inventory -d inventory_db --clean --if-exists > "$BACKUP_PATH"; then
    
    # Get file size
    backup_size=$(du -h "$BACKUP_PATH" | cut -f1)
    
    echo -e "${GREEN}✓ Backup created successfully!${NC}"
    echo -e "  File: ${YELLOW}${BACKUP_PATH}${NC}"
    echo -e "  Size: ${YELLOW}${backup_size}${NC}"
    
    # Compress backup
    echo -e "${YELLOW}Compressing backup...${NC}"
    if gzip "$BACKUP_PATH"; then
        compressed_size=$(du -h "${BACKUP_PATH}.gz" | cut -f1)
        echo -e "${GREEN}✓ Backup compressed successfully${NC}"
        echo -e "  Compressed size: ${YELLOW}${compressed_size}${NC}"
        BACKUP_PATH="${BACKUP_PATH}.gz"
    else
        echo -e "${YELLOW}Warning: Compression failed, keeping uncompressed backup${NC}"
    fi
    
    # Clean up old backups
    if [ "$RETENTION_DAYS" -gt 0 ]; then
        echo -e "${YELLOW}Cleaning up backups older than ${RETENTION_DAYS} days...${NC}"
        find "$BACKUP_DIR" -name "backup_*.sql*" -type f -mtime +$RETENTION_DAYS -delete
        remaining_backups=$(find "$BACKUP_DIR" -name "backup_*.sql*" -type f | wc -l)
        echo -e "${GREEN}Retained backups: ${remaining_backups}${NC}"
    fi
    
    # List recent backups
    echo -e "\n${GREEN}Recent backups:${NC}"
    ls -lh "$BACKUP_DIR"/backup_*.sql* | tail -5 | awk '{print "  " $9 " (" $5 ")"}'
    
else
    echo -e "${RED}✗ Backup failed${NC}"
    exit 1
fi

echo -e "\n${GREEN}Backup completed successfully!${NC}"