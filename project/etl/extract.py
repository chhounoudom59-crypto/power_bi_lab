import psycopg2
import pandas as pd
from sqlalchemy import create_engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Extractor:
    def __init__(self, source_config, staging_config):
        self.source_engine = create_engine(
            f"postgresql://{source_config['user']}:{source_config['password']}@"
            f"{source_config['host']}:{source_config['port']}/{source_config['database']}"
        )
        self.staging_engine = create_engine(
            f"postgresql://{staging_config['user']}:{staging_config['password']}@"
            f"{staging_config['host']}:{staging_config['port']}/{staging_config['database']}"
        )
    
    def extract_table(self, table_name, schema='public'):
        """Extract table from source database"""
        try:
            query = f'SELECT * FROM {schema}."{table_name}"'
            logger.info(f"Extracting {table_name}...")
            df = pd.read_sql(query, self.source_engine)
            logger.info(f"Extracted {len(df)} rows from {table_name}")
            return df
        except Exception as e:
            logger.error(f"Error extracting {table_name}: {e}")
            return pd.DataFrame()
    
    def load_to_staging(self, df, table_name):
        """Load data to staging PostgreSQL"""
        if df.empty:
            logger.warning(f"No data to load for {table_name}")
            return
        try:
            df.to_sql(f'stg_{table_name}', self.staging_engine, 
                      if_exists='replace', index=False)
            logger.info(f"Loaded {len(df)} rows to stg_{table_name}")
        except Exception as e:
            logger.error(f"Error loading {table_name}: {e}")
    
    def extract_all_tables(self):
        """Extract all relevant tables"""
        tables = [
            'Student', 'Teacher', 'Course', 'Class', 'Enroll', 
            'Attendance', 'Score', 'Schedule', 'ScheduleTimes', 
            'Semester', 'Department', 'Faculty', 'Major', 'User'
        ]
        
        for table in tables:
            df = self.extract_table(table)
            self.load_to_staging(df, table)
        
        logger.info("All tables extracted successfully!")
        return True