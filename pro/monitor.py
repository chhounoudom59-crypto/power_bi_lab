"""
Monitoring Dashboard for ETL Pipeline
Provides real-time insights into pipeline health and performance
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
from typing import Dict, List
import pandas as pd

logger = logging.getLogger(__name__)


class ETLMonitor:
    """Monitor ETL pipeline execution and health"""
    
    def __init__(self, log_file: str = 'etl_pipeline.log'):
        """Initialize monitor"""
        self.log_file = log_file
        self.metrics_db = 'etl_metrics.db'
        self._init_metrics_db()
    
    def _init_metrics_db(self):
        """Initialize metrics SQLite database"""
        conn = sqlite3.connect(self.metrics_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pipeline_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_timestamp TIMESTAMP,
                status TEXT,
                tables_processed INT,
                rows_extracted INT,
                rows_loaded INT,
                duration_seconds INT,
                error_message TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def parse_logs(self) -> List[Dict]:
        """Parse ETL log file for metrics"""
        metrics = []
        
        if not Path(self.log_file).exists():
            logger.warning(f"Log file not found: {self.log_file}")
            return metrics
        
        with open(self.log_file, 'r') as f:
            for line in f:
                # Parse log lines and extract metrics
                if 'ETL Pipeline completed successfully' in line:
                    # Extract timestamp and mark as successful
                    pass
        
        return metrics
    
    def record_metrics(self, 
                      status: str,
                      tables_processed: int = 0,
                      rows_extracted: int = 0,
                      rows_loaded: int = 0,
                      duration_seconds: int = 0,
                      error_message: str = None):
        """Record pipeline execution metrics"""
        
        conn = sqlite3.connect(self.metrics_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO pipeline_metrics 
            (run_timestamp, status, tables_processed, rows_extracted, 
             rows_loaded, duration_seconds, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now(),
            status,
            tables_processed,
            rows_extracted,
            rows_loaded,
            duration_seconds,
            error_message
        ))
        
        conn.commit()
        conn.close()
    
    def get_execution_stats(self, days: int = 7) -> Dict:
        """Get execution statistics for last N days"""
        
        conn = sqlite3.connect(self.metrics_db)
        query = f'''
            SELECT 
                COUNT(*) as total_runs,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_runs,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_runs,
                AVG(duration_seconds) as avg_duration,
                SUM(rows_loaded) as total_rows_loaded,
                AVG(rows_loaded) as avg_rows_loaded
            FROM pipeline_metrics
            WHERE run_timestamp >= datetime('now', '-{days} days')
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df.to_dict(orient='records')[0] if not df.empty else {}
    
    def get_recent_runs(self, limit: int = 10) -> pd.DataFrame:
        """Get recent pipeline executions"""
        
        conn = sqlite3.connect(self.metrics_db)
        query = '''
            SELECT * FROM pipeline_metrics
            ORDER BY run_timestamp DESC
            LIMIT ?
        '''
        
        df = pd.read_sql_query(query, conn, params=(limit,))
        conn.close()
        
        return df
    
    def generate_report(self) -> str:
        """Generate ETL performance report"""
        
        stats = self.get_execution_stats()
        recent = self.get_recent_runs()
        
        report = f"""
        ╔══════════════════════════════════════════════════════════╗
        ║          ETL PIPELINE EXECUTION REPORT                   ║
        ║          Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}          ║
        ╚══════════════════════════════════════════════════════════╝
        
        📊 EXECUTION STATISTICS (Last 7 Days)
        ─────────────────────────────────────
        ✓ Successful Runs:     {stats.get('successful_runs', 0)}
        ✗ Failed Runs:         {stats.get('failed_runs', 0)}
        ⏱ Average Duration:    {stats.get('avg_duration', 0):.0f} seconds
        📦 Total Rows Loaded:  {stats.get('total_rows_loaded', 0):,}
        
        📈 RECENT EXECUTIONS
        ───────────────────
        """
        
        for idx, row in recent.iterrows():
            status_icon = "✓" if row['status'] == 'success' else "✗"
            report += f"\n{status_icon} {row['run_timestamp']} | Status: {row['status']} | Rows: {row['rows_loaded']}"
        
        report += "\n\n" + "="*60 + "\n"
        
        return report
    
    def check_health(self) -> Dict:
        """Check pipeline health status"""
        
        stats = self.get_execution_stats(days=1)
        recent = self.get_recent_runs(limit=1)
        
        health = {
            'status': 'healthy',
            'last_run': None,
            'issues': []
        }
        
        if not recent.empty:
            last_run = recent.iloc[0]
            health['last_run'] = {
                'timestamp': last_run['run_timestamp'],
                'status': last_run['status'],
                'duration': last_run['duration_seconds']
            }
            
            # Check for issues
            if last_run['status'] == 'failed':
                health['status'] = 'warning'
                health['issues'].append('Last run failed')
            
            # Check if last run was recent (within last 26 hours for daily schedule)
            last_run_time = datetime.fromisoformat(last_run['run_timestamp'])
            if datetime.now() - last_run_time > timedelta(hours=26):
                health['status'] = 'critical'
                health['issues'].append('No recent successful execution')
        else:
            health['status'] = 'critical'
            health['issues'].append('No execution history found')
        
        return health


def print_dashboard():
    """Print real-time monitoring dashboard"""
    
    monitor = ETLMonitor()
    
    while True:
        import os
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print(monitor.generate_report())
        
        # Check health
        health = monitor.check_health()
        print(f"\n🏥 PIPELINE HEALTH: {health['status'].upper()}")
        
        if health['issues']:
            print("⚠️  Issues detected:")
            for issue in health['issues']:
                print(f"   - {issue}")
        
        # Wait before refresh
        import time
        print("\n[Refreshing in 60 seconds... Press Ctrl+C to exit]")
        time.sleep(60)


if __name__ == "__main__":
    print_dashboard()
