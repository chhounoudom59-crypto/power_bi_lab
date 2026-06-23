"""
Apache Airflow DAG for ETL Pipeline Orchestration
Production-ready DAG for scheduled data warehouse updates
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
from datetime import datetime, timedelta
import json
import sys
sys.path.append('/path/to/bitest/pro')  # Update path

from etl_pipeline import ETLPipeline

# DAG configuration
default_args = {
    'owner': 'data_team',
    'start_date': days_ago(1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email': ['alerts@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
}

dag = DAG(
    'postgres_to_datawarehouse_etl',
    default_args=default_args,
    description='Automated ETL: PostgreSQL → Data Warehouse',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    catchup=False,
    tags=['etl', 'data-warehouse']
)

# Load configuration
def load_config(**context):
    """Load ETL configuration"""
    config_path = Variable.get('etl_config_path', '/path/to/config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

# Extract task
def extract_data(**context):
    """Extract data from source"""
    config = load_config(**context)
    pipeline = ETLPipeline(config['source'], config['target'])
    
    if not pipeline.connect_source():
        raise Exception("Failed to connect to source")
    
    data = pipeline.extract(tables=config['pipeline'].get('tables'))
    
    # Store in XCom for next task
    context['task_instance'].xcom_push(key='extracted_data', value=data)
    
    return f"Extracted {len(data)} tables"

# Transform task
def transform_data(**context):
    """Transform extracted data"""
    config = load_config(**context)
    
    # Get extracted data from previous task
    ti = context['task_instance']
    data = ti.xcom_pull(task_ids='extract_data', key='extracted_data')
    
    if not data:
        raise Exception("No data to transform")
    
    pipeline = ETLPipeline(config['source'], config['target'])
    transformed_data = pipeline.transform(data)
    
    # Store in XCom for next task
    ti.xcom_push(key='transformed_data', value=transformed_data)
    
    return f"Transformed {len(transformed_data)} tables"

# Load task
def load_data(**context):
    """Load data to warehouse"""
    config = load_config(**context)
    
    # Get transformed data from previous task
    ti = context['task_instance']
    data = ti.xcom_pull(task_ids='transform_data', key='transformed_data')
    
    if not data:
        raise Exception("No data to load")
    
    pipeline = ETLPipeline(config['source'], config['target'])
    
    if not pipeline.connect_target():
        raise Exception("Failed to connect to target")
    
    success = pipeline.load(data, mode=config['pipeline'].get('mode', 'replace'))
    
    if not success:
        raise Exception("Load failed")
    
    return f"Loaded {len(data)} tables"

# Health check task
def health_check(**context):
    """Verify data warehouse health"""
    config = load_config(**context)
    pipeline = ETLPipeline(config['source'], config['target'])
    
    if not pipeline.connect_target():
        raise Exception("Data warehouse health check failed")
    
    return "✓ Data warehouse is healthy"

# Define tasks
task_extract = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    provide_context=True,
    dag=dag
)

task_transform = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    provide_context=True,
    dag=dag
)

task_load = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    provide_context=True,
    dag=dag
)

task_health_check = PythonOperator(
    task_id='health_check',
    python_callable=health_check,
    provide_context=True,
    dag=dag
)

# Define dependencies
task_extract >> task_transform >> task_load >> task_health_check
