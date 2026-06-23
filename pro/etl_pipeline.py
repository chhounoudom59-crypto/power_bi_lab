"""
ETL Pipeline: PostgreSQL → Data Warehouse
Automates extraction, transformation, and loading of data
"""

import pandas as pd
import logging
from datetime import datetime
from sqlalchemy import create_engine, inspect, MetaData, Table
from typing import Dict, List, Optional
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ETLPipeline:
    """Main ETL Pipeline class for data warehouse automation"""
    
    def __init__(self, source_config: Dict, target_config: Dict):
        """
        Initialize ETL Pipeline
        
        Args:
            source_config: PostgreSQL source connection config
            target_config: Data Warehouse target connection config
        """
        self.source_config = source_config
        self.target_config = target_config
        self.source_engine = None
        self.target_engine = None
        self.metadata = {}
        
    def connect_source(self) -> bool:
        """Connect to source PostgreSQL database"""
        try:
            port = self.source_config.get('port', 5432)
            conn_string = (
                f"postgresql+psycopg2://{self.source_config['user']}:"
                f"{self.source_config['password']}@{self.source_config['host']}:{port}/"
                f"{self.source_config['database']}"
            )
            self.source_engine = create_engine(conn_string)
            
            # Test connection
            with self.source_engine.connect() as conn:
                conn.execute("SELECT 1")
            
            logger.info(f"✓ Connected to source: {self.source_config['host']}/{self.source_config['database']}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to connect to source: {e}")
            return False
    
    def connect_target(self) -> bool:
        """Connect to target Data Warehouse"""
        try:
            if self.target_config['type'] == 'postgresql':
                port = self.target_config.get('port', 5432)
                conn_string = (
                    f"postgresql+psycopg2://{self.target_config['user']}:"
                    f"{self.target_config['password']}@{self.target_config['host']}:{port}/"
                    f"{self.target_config['database']}"
                )
            elif self.target_config['type'] == 'snowflake':
                # Snowflake connection (requires snowflake-sqlalchemy)
                conn_string = (
                    f"snowflake://{self.target_config['user']}:"
                    f"{self.target_config['password']}@{self.target_config['account']}"
                )
            else:
                logger.error(f"Unsupported target type: {self.target_config['type']}")
                return False
            
            self.target_engine = create_engine(conn_string)
            
            # Test connection
            with self.target_engine.connect() as conn:
                conn.execute("SELECT 1")
            
            logger.info(f"✓ Connected to target: {self.target_config['type']}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to connect to target: {e}")
            return False
    
    def extract(self, tables: Optional[List[str]] = None) -> Dict[str, pd.DataFrame]:
        """
        Extract data from source PostgreSQL
        
        Args:
            tables: List of table names to extract. If None, extracts all tables
            
        Returns:
            Dictionary of DataFrames {table_name: dataframe}
        """
        if not self.source_engine:
            logger.error("Source engine not initialized")
            return {}
        
        data = {}
        
        try:
            # Get list of tables
            if tables is None:
                inspector = inspect(self.source_engine)
                tables = inspector.get_table_names()
                logger.info(f"Found {len(tables)} tables to extract")
            
            # Extract each table
            for table in tables:
                try:
                    logger.info(f"Extracting table: {table}")
                    df = pd.read_sql_table(table, self.source_engine)
                    data[table] = df
                    logger.info(f"  ✓ Extracted {len(df)} rows from {table}")
                except Exception as e:
                    logger.error(f"  ✗ Failed to extract {table}: {e}")
            
            logger.info(f"✓ Extraction complete: {len(data)} tables")
            return data
            
        except Exception as e:
            logger.error(f"✗ Extraction failed: {e}")
            return {}
    
    def transform(self, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Transform data (add timestamps, data quality checks, etc.)
        
        Args:
            data: Dictionary of DataFrames
            
        Returns:
            Transformed dictionary of DataFrames
        """
        logger.info("Starting transformation...")
        
        for table_name, df in data.items():
            try:
                # Add metadata columns
                df['_extracted_at'] = datetime.now()
                df['_processed_at'] = None  # Will be filled on load
                
                # Data quality checks
                logger.info(f"  Checking data quality for {table_name}")
                
                # Remove duplicates (if applicable)
                initial_rows = len(df)
                df = df.drop_duplicates()
                removed = initial_rows - len(df)
                if removed > 0:
                    logger.info(f"    - Removed {removed} duplicate rows")
                
                # Handle null values (example: fill with 'UNKNOWN' for string columns)
                for col in df.select_dtypes(include=['object']).columns:
                    null_count = df[col].isnull().sum()
                    if null_count > 0:
                        logger.info(f"    - {col}: {null_count} null values")
                
                data[table_name] = df
                logger.info(f"  ✓ Transformed {table_name}")
                
            except Exception as e:
                logger.error(f"  ✗ Transformation failed for {table_name}: {e}")
        
        logger.info("✓ Transformation complete")
        return data
    
    def load(self, data: Dict[str, pd.DataFrame], mode: str = 'replace') -> bool:
        """
        Load data to target Data Warehouse
        
        Args:
            data: Dictionary of DataFrames
            mode: 'replace' (replace table) or 'append' (append to table)
            
        Returns:
            Success status
        """
        if not self.target_engine:
            logger.error("Target engine not initialized")
            return False
        
        try:
            logger.info(f"Starting load (mode: {mode})...")
            
            for table_name, df in data.items():
                try:
                    # Update processed timestamp
                    df['_processed_at'] = datetime.now()
                    
                    # Load to target
                    logger.info(f"Loading table: {table_name} ({len(df)} rows)")
                    df.to_sql(
                        name=table_name,
                        con=self.target_engine,
                        if_exists=mode,
                        index=False,
                        chunksize=1000
                    )
                    logger.info(f"  ✓ Loaded {table_name}")
                    
                except Exception as e:
                    logger.error(f"  ✗ Failed to load {table_name}: {e}")
                    return False
            
            logger.info("✓ Load complete")
            return True
            
        except Exception as e:
            logger.error(f"✗ Load failed: {e}")
            return False
    
    def run_pipeline(
        self, 
        tables: Optional[List[str]] = None,
        mode: str = 'replace'
    ) -> bool:
        """
        Run complete ETL pipeline
        
        Args:
            tables: Tables to extract (None = all)
            mode: Load mode ('replace' or 'append')
            
        Returns:
            Success status
        """
        logger.info("=" * 60)
        logger.info("Starting ETL Pipeline")
        logger.info("=" * 60)
        
        # Connect
        if not self.connect_source():
            return False
        if not self.connect_target():
            return False
        
        # Extract
        data = self.extract(tables)
        if not data:
            logger.error("No data extracted")
            return False
        
        # Transform
        data = self.transform(data)
        
        # Load
        success = self.load(data, mode)
        
        if success:
            logger.info("=" * 60)
            logger.info("✓ ETL Pipeline completed successfully")
            logger.info("=" * 60)
        else:
            logger.error("ETL Pipeline failed")
        
        return success


def load_config(config_file: str) -> Dict:
    """Load configuration from JSON file"""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}


if __name__ == "__main__":
    import sys
    
    # Load configuration from JSON file
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'config.json'
    config = load_config(config_file)
    
    if not config:
        logger.error("Failed to load configuration")
        exit(1)
    
    # Initialize and run pipeline
    pipeline = ETLPipeline(config['source'], config['target'])
    success = pipeline.run_pipeline(
        tables=config['pipeline'].get('tables'),  # None = all tables
        mode=config['pipeline'].get('mode', 'replace')  # 'replace' or 'append'
    )
    
    exit(0 if success else 1)
