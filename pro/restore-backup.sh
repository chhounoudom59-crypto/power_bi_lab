#!/bin/bash
# Download and Restore PostgreSQL Backup
# This script downloads the backup from S3 and restores it to the source database

set -e

BACKUP_URL="https://pub-f8f15af25ba94a7ca801f4857d2bbf07.r2.dev/backup/database.sql"
BACKUP_FILE="database_backup.sql"
CONTAINER_NAME="etl_source_db"
DB_HOST="localhost"
DB_PORT="5432"
DB_USER="postgres"
DB_NAME="lms-prod"

echo "╔════════════════════════════════════════════╗"
echo "║   PostgreSQL Backup Restore                ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check if Docker is running
echo "🔍 Checking Docker..."
if ! docker ps &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Check if PostgreSQL container is running
echo "🔍 Checking PostgreSQL container..."
if ! docker ps --filter "name=$CONTAINER_NAME" --format '{{.Names}}' | grep -q "$CONTAINER_NAME"; then
    echo "❌ PostgreSQL container is not running."
    echo "   Start it with: docker-compose up -d postgres_source"
    exit 1
fi

echo "✓ PostgreSQL container is running"
echo ""

# Download backup
echo "📥 Downloading backup from S3..."
if [ -f "$BACKUP_FILE" ]; then
    echo "   Backup already exists. Skipping download..."
else
    curl -L -o "$BACKUP_FILE" "$BACKUP_URL"
    if [ $? -ne 0 ]; then
        echo "❌ Failed to download backup"
        exit 1
    fi
    echo "✓ Backup downloaded: $BACKUP_FILE"
fi

echo ""

# Check backup file size
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "📊 Backup file size: $BACKUP_SIZE"
echo ""

# Restore to PostgreSQL
echo "🔄 Restoring database..."
echo "   Container: $CONTAINER_NAME"
echo "   Database: $DB_NAME"
echo ""

# Copy backup to container
docker cp "$BACKUP_FILE" "$CONTAINER_NAME:/tmp/$BACKUP_FILE"

# Restore database
docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -f "/tmp/$BACKUP_FILE" > /dev/null 2>&1 || {
    echo "⚠️  Database may already exist or backup format issue"
    echo "   Attempting to restore with error handling..."
    
    # Try dropping and recreating database
    docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -c "DROP DATABASE IF EXISTS $DB_NAME;" || true
    docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;" || true
    docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -f "/tmp/$BACKUP_FILE" > /dev/null 2>&1
}

echo "✓ Database restored successfully"
echo ""

# Verify restoration
echo "✓ Verifying restoration..."
TABLE_COUNT=$(docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" -t | tr -d ' ')

echo "   Tables found: $TABLE_COUNT"
echo ""

# Cleanup
rm -f "$BACKUP_FILE"
echo "✓ Backup file cleaned up"
echo ""

echo "✅ Database restoration complete!"
echo ""
echo "🔗 Connection details:"
echo "   Host: localhost"
echo "   Port: 5432"
echo "   Database: $DB_NAME"
echo "   User: postgres"
echo "   Password: postgres_source_password"
echo ""
echo "📝 Next steps:"
echo "   1. Run ETL: docker-compose run --rm etl_pipeline python etl_pipeline.py docker-config.json"
echo "   2. Check logs: docker-compose logs -f etl_pipeline"
echo "   3. Access PgAdmin: http://localhost:5050"
