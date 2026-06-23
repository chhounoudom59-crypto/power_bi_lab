# ETL Pipeline - Quick Start Guide

## 🚀 QUICK START (5 minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Setup Data Warehouse
```bash
psql -U postgres -f setup_data_warehouse.sql
```

### Step 3: Configure Credentials
Edit `config.json`:
```json
{
  "source": {
    "password": "YOUR_POSTGRES_PASSWORD"
  },
  "target": {
    "password": "YOUR_POSTGRES_PASSWORD"
  }
}
```

### Step 4: Test Pipeline (One-time run)
```bash
python etl_pipeline.py
```

### Step 5: Schedule Automation

**Option A: Windows Task Scheduler (Recommended for Windows)**
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup_scheduler.ps1
```

**Option B: Python Scheduler (Cross-platform)**
```bash
python scheduler.py config.json
# Keep terminal open (or run in background)
```

**Option C: Manual Batch File**
- Double-click `run_etl.bat` to execute manually
- Logs saved to `etl_execution.log`

---

## 📊 Monitor Pipeline

View real-time dashboard:
```bash
python monitor.py
```

View execution logs:
```bash
tail -f etl_pipeline.log
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| PostgreSQL connection failed | Check `config.json` credentials and `psql` status |
| No tables found | Verify database name and schema in config |
| Task not running | Check Windows Task Scheduler, enable network access |
| Performance slow | Use `mode: 'append'` for large tables |

---

## 📈 Next: Connect Power BI

1. **Add Connection in Power BI Desktop:**
   - Get Data → PostgreSQL Database
   - Server: `localhost`
   - Database: `data_warehouse`
   - Credentials: Your PostgreSQL user/password

2. **Import Tables:**
   - Select tables from data warehouse
   - Create visualizations/dashboards

---

## Architecture

```
PostgreSQL (Source)
    ↓
etl_pipeline.py (Extract → Transform → Load)
    ↓
data_warehouse (Target)
    ↓
Power BI / Analytics
```

**Automation:**
- Windows: Task Scheduler (setup_scheduler.ps1)
- Linux/Mac: Cron + scheduler.py
- Enterprise: Apache Airflow (airflow_dag.py)

---

## Files Reference

- `etl_pipeline.py` - Main ETL logic
- `scheduler.py` - Scheduling engine
- `config.json` - Configuration (EDIT THIS!)
- `monitor.py` - Health monitoring dashboard
- `requirements.txt` - Python dependencies
- `setup_scheduler.ps1` - Windows Task Scheduler setup

Good luck! 🎉
