# Database configurations
SOURCE_DB = {
    'host': 'localhost',
    'port': 5434,  # Your source PostgreSQL port
    'database': 'app_db',  # Your database name
    'user': 'admin',
    'password': 'admin'  # Update with your password
}

STAGING_DB = {
    'host': 'localhost',
    'port': 5434,  # Same as source for now
    'database': 'app_db',
    'user': 'admin',
    'password': 'admin'
}

WAREHOUSE_DB = {
    'host': 'localhost',
    'port': 5433,  # Your warehouse port
    'database': 'warehouse',
    'user': 'admin',
    'password': 'admin'  # Update with your password
}

# ETL Settings
BATCH_SIZE = 10000
LOG_LEVEL = 'INFO'