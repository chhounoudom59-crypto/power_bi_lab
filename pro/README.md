# ETL Pipeline Automation Setup Guide

## Project Structure
```
bitest/pro/
├── etl_pipeline.py          # Main ETL pipeline class
├── scheduler.py             # Scheduler for automation
├── config.json              # Configuration file (EDIT THIS)
├── requirements.txt         # Python dependencies
├── test.ipynb               # Testing notebook
├── setup_data_warehouse.sql # Create target DW schema
└── README.md                # This file
```

---

## 1. Prerequisites

### Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Create Data Warehouse in PostgreSQL
```bash
psql -U postgres -f setup_data_warehouse.sql
```

---

## 2. Configuration (IMPORTANT)

Edit `config.json` with your credentials:

```json
{
  "source": {
    "host": "localhost",
    "database": "lms-prod",
    "user": "postgres",
    "password": "YOUR_PASSWORD"
  },
  "target": {
    "host": "localhost",
    "database": "data_warehouse",
    "user": "postgres",
    "password": "YOUR_PASSWORD"
  },
  "pipeline": {
    "schedule": "daily",
    "time": "02:00"
  }
}
```

---

## 3. Quick Start

### Option A: Run Once
```bash
python etl_pipeline.py
```

### Option B: Schedule (Automated)
```bash
# Daily at 2 AM
python scheduler.py config.json

# In Windows Task Scheduler or cron:
# crontab: 0 2 * * * cd /path/to/pro && python scheduler.py config.json
```

---

## 4. Pipeline Architecture

```
PostgreSQL (lms-prod)
    ↓
[EXTRACT] - Read all/specific tables
    ↓
[TRANSFORM] - Add timestamps, clean data
    ↓
[LOAD] - Write to data_warehouse
    ↓
Analytics Ready
```

### Monitoring
- Logs: `etl_pipeline.log` (detailed execution)
- Scheduler logs: `scheduler.log` (schedule events)

---

## 5. Advanced: Airflow Integration

For enterprise scheduling, use Apache Airflow:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from etl_pipeline import ETLPipeline
import json

default_args = {
    'owner': 'data_team',
    'start_date': datetime(2024, 1, 1),
    'retries': 2,
}

dag = DAG('etl_pipeline', default_args=default_args, schedule_interval='0 2 * * *')

def run_etl():
    with open('config.json') as f:
        config = json.load(f)
    pipeline = ETLPipeline(config['source'], config['target'])
    pipeline.run_pipeline()

task = PythonOperator(task_id='run_etl', python_callable=run_etl, dag=dag)
```

---

## 6. Monitoring & Alerts

Add email notifications for failures (optional):

```python
import smtplib
from email.mime.text import MIMEText

def send_alert(subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = 'etl@yourcompany.com'
    msg['To'] = 'alerts@yourcompany.com'
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('user@gmail.com', 'password')
        server.send_message(msg)
```

---

## 7. Troubleshooting

### Connection Failed
```bash
# Test PostgreSQL connection
psql -h localhost -U postgres -d lms-prod
# Check credentials in config.json
```

### No Data Extracted
```bash
# Check table names in source DB
psql -U postgres -d lms-prod -c "\dt"
# Verify schema in config.json
```

### Performance Issues
- Use `mode: 'append'` for large tables instead of `replace`
- Schedule during off-peak hours
- Add indexes on frequently queried columns

---

## 8. Next Steps

1. ✅ Edit `config.json` with your database credentials
2. ✅ Run once: `python etl_pipeline.py`
3. ✅ Schedule: `python scheduler.py config.json`
4. ✅ Monitor logs for success/failures
5. ✅ Connect Power BI to `data_warehouse` for visualization

---

## Support

For issues, check:
- `etl_pipeline.log` - detailed execution logs
- PostgreSQL error logs
- Task Scheduler/Cron logs (for automated runs)

Good luck with your data warehouse! 🚀
