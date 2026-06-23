import psycopg2
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.config import WAREHOUSE_DB

def init_warehouse():
    """Initialize warehouse database with schema"""
    try:
        # Connect to postgres database first
        conn = psycopg2.connect(
            host=WAREHOUSE_DB['host'],
            port=WAREHOUSE_DB['port'],
            user=WAREHOUSE_DB['user'],
            password=WAREHOUSE_DB['password'],
            database='postgres'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create warehouse database if not exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{WAREHOUSE_DB['database']}'")
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {WAREHOUSE_DB['database']}")
            print(f"Database '{WAREHOUSE_DB['database']}' created")
        
        cursor.close()
        conn.close()
        
        # Connect to warehouse database and run schema
        conn = psycopg2.connect(
            host=WAREHOUSE_DB['host'],
            port=WAREHOUSE_DB['port'],
            user=WAREHOUSE_DB['user'],
            password=WAREHOUSE_DB['password'],
            database=WAREHOUSE_DB['database']
        )
        cursor = conn.cursor()
        
        # Read and execute schema SQL
        with open('warehouse/schema.sql', 'r') as f:
            schema_sql = f.read()
            cursor.execute(schema_sql)
        
        conn.commit()
        print("Warehouse schema created successfully!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Failed to initialize warehouse: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_warehouse()