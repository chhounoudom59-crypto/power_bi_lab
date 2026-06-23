#!/bin/bash
# Complete End-to-End ETL Workflow
# 1. Start Docker services
# 2. Download and restore backup
# 3. Run ETL pipeline
# 4. Verify results

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   ETL Pipeline - Complete End-to-End Workflow              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Start Docker services
echo "═══════════════════════════════════════════════════════════"
echo "STEP 1: Starting Docker Services"
echo "═══════════════════════════════════════════════════════════"
echo ""

echo "🚀 Starting Docker services..."
docker-compose up -d

echo "⏳ Waiting for services to be healthy..."
sleep 15

echo ""
echo "📊 Service Status:"
docker-compose ps
echo ""

# Step 2: Download and restore backup
echo "═══════════════════════════════════════════════════════════"
echo "STEP 2: Downloading and Restoring Backup"
echo "═══════════════════════════════════════════════════════════"
echo ""

BACKUP_URL="https://pub-f8f15af25ba94a7ca801f4857d2bbf07.r2.dev/backup/database.sql"
BACKUP_FILE="database_backup.sql"
CONTAINER_NAME="etl_source_db"
DB_USER="postgres"
DB_NAME="lms-prod"

echo "📥 Downloading backup..."
curl -L -o "$BACKUP_FILE" "$BACKUP_URL"
echo "✓ Backup downloaded"
echo ""

echo "🔄 Restoring to PostgreSQL..."
docker cp "$BACKUP_FILE" "$CONTAINER_NAME:/tmp/$BACKUP_FILE"
docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -f "/tmp/$BACKUP_FILE" > /dev/null 2>&1 || {
    docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -c "DROP DATABASE IF EXISTS $DB_NAME;" || true
    docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;" || true
    docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -f "/tmp/$BACKUP_FILE" > /dev/null 2>&1
}

echo "✓ Database restored"
echo ""

# Verify
TABLE_COUNT=$(docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" -t | tr -d ' ')
echo "📊 Tables loaded: $TABLE_COUNT"

rm -f "$BACKUP_FILE"
echo ""

# Step 3: Run ETL Pipeline
echo "═══════════════════════════════════════════════════════════"
echo "STEP 3: Running ETL Pipeline"
echo "═══════════════════════════════════════════════════════════"
echo ""

echo "🔄 Executing ETL Pipeline..."
docker-compose run --rm etl_pipeline python etl_pipeline.py docker-config.json

echo ""
echo "✓ ETL Pipeline completed"
echo ""

# Step 4: Verify results
echo "═══════════════════════════════════════════════════════════"
echo "STEP 4: Verifying Results"
echo "═══════════════════════════════════════════════════════════"
echo ""

echo "📊 Source Database Tables:"
docker exec etl_source_db psql -U postgres -d lms-prod -c "
SELECT table_name, 
       (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = 'public' AND table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
ORDER BY table_name;"

echo ""
echo "📊 Target Database Tables:"
docker exec etl_target_db psql -U postgres -d data_warehouse -c "
SELECT table_name, 
       (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = 'public' AND table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
ORDER BY table_name;"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ ETL Workflow Complete!"
echo "═══════════════════════════════════════════════════════════"
echo ""

echo "🌐 Access Points:"
echo "   • Source DB:  localhost:5432 (lms-prod)"
echo "   • Target DB:  localhost:5433 (data_warehouse)"
echo "   • PgAdmin:    http://localhost:5050"
echo "   • Logs:       docker-compose logs -f"
echo ""

echo "📊 Next: Connect Power BI to localhost:5433 (data_warehouse)"
echo "   See POWER_BI_GUIDE.md for detailed instructions"
echo ""

echo "🛑 To stop services: docker-compose down"
