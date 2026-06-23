from sqlalchemy import create_engine, text
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class Loader:
    def __init__(self, warehouse_config):
        self.engine = create_engine(
            f"postgresql://{warehouse_config['user']}:{warehouse_config['password']}@"
            f"{warehouse_config['host']}:{warehouse_config['port']}/{warehouse_config['database']}",
            connect_args={'options': '-csearch_path=warehouse'}
        )
    
    def load_table(self, df, table_name):
        """Load table with append logic"""
        if df.empty:
            logger.warning(f"No data to load for {table_name}")
            return
        
        with self.engine.begin() as conn:
            # We assume tables are truncated or empty if running a fresh batch, 
            # or handling of duplicates is done prior. 
            # For this pipeline rebuild, we append.
            df.to_sql(table_name, conn, if_exists='append', index=False)
            logger.info(f"Loaded {len(df)} rows to {table_name}")
    