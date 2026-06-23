from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.sensors.postgres import PostgresSensor
from datetime import datetime, timedelta
import sys
import os

# Add project to path
sys.path.append('/opt/airflow/etl_project')

from etl.main import main as run_etl
from etl.config import WAREHOUSE_DB

default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'email': ['data-team@company.com'],
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=3)
}

# Define DAG
dag = DAG(
    'lms_etl_pipeline',
    default_args=default_args,
    description='Complete ETL pipeline for LMS Data Warehouse',
    schedule_interval='0 1 * * *',  # Daily at 1 AM
    catchup=False,
    tags=['lms', 'etl', 'warehouse'],
    max_active_runs=1
)

# Task 1: Check source database availability
check_source_db = PostgresSensor(
    task_id='check_source_db',
    postgres_conn_id='source_db',
    sql='SELECT 1',
    poke_interval=30,
    timeout=300,
    dag=dag
)

# Task 2: Check warehouse database availability
check_warehouse_db = PostgresSensor(
    task_id='check_warehouse_db',
    postgres_conn_id='warehouse_db',
    sql='SELECT 1',
    poke_interval=30,
    timeout=300,
    dag=dag
)

# Task 3: Run ETL pipeline
run_etl_task = PythonOperator(
    task_id='run_etl_pipeline',
    python_callable=run_etl,
    dag=dag
)

# Task 4: Validate row counts
validate_row_counts = PostgresOperator(
    task_id='validate_row_counts',
    postgres_conn_id='warehouse_db',
    sql="""
        WITH validation AS (
            SELECT 
                'dim_student' as table_name,
                COUNT(*) as row_count
            FROM dim_student
            UNION ALL
            SELECT 
                'fact_attendance',
                COUNT(*)
            FROM fact_attendance
            UNION ALL
            SELECT 
                'fact_enrollment',
                COUNT(*)
            FROM fact_enrollment
        )
        SELECT 
            table_name,
            row_count,
            CASE 
                WHEN row_count > 0 THEN 'PASS'
                ELSE 'FAIL'
            END as status
        FROM validation;
    """,
    dag=dag
)

# Task 5: Check data quality
check_data_quality = PostgresOperator(
    task_id='check_data_quality',
    postgres_conn_id='warehouse_db',
    sql="""
        -- Check for NULL foreign keys
        SELECT 
            'fact_attendance' as table_name,
            COUNT(*) as null_count
        FROM fact_attendance
        WHERE student_sk IS NULL OR schedule_time_sk IS NULL
        
        UNION ALL
        
        -- Check for invalid GPA
        SELECT 
            'fact_score' as table_name,
            COUNT(*) as null_count
        FROM fact_score
        WHERE gpa < 0 OR gpa > 4.0;
    """,
    dag=dag
)

# Task 6: Refresh materialized views
refresh_views = PostgresOperator(
    task_id='refresh_materialized_views',
    postgres_conn_id='warehouse_db',
    sql="""
        REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_attendance;
        REFRESH MATERIALIZED VIEW CONCURRENTLY mv_semester_gpa;
    """,
    dag=dag
)

# Task 7: Send success notification
send_success_email = EmailOperator(
    task_id='send_success_email',
    to=['admin@company.com', 'data-team@company.com'],
    subject='LMS ETL Pipeline - Success',
    html_content="""
        <h2>✅ ETL Pipeline Completed Successfully</h2>
        <p><strong>Date:</strong> {{ ds }}</p>
        <p><strong>Execution Time:</strong> {{ execution_date }}</p>
        <h3>Summary:</h3>
        <ul>
            <li>All tables extracted successfully</li>
            <li>Data quality checks passed</li>
            <li>Warehouse updated</li>
            <li>Materialized views refreshed</li>
        </ul>
        <p>Next run scheduled for: {{ next_execution_date }}</p>
    """,
    dag=dag
)

# Task 8: Cleanup old logs
cleanup_logs = BashOperator(
    task_id='cleanup_logs',
    bash_command='find /opt/airflow/logs -type f -mtime +30 -delete',
    dag=dag
)

# Define dependencies
check_source_db >> check_warehouse_db >> run_etl_task
run_etl_task >> validate_row_counts >> check_data_quality >> refresh_views
refresh_views >> send_success_email >> cleanup_logs