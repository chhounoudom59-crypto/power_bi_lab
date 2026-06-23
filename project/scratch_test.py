import pandas as pd
from sqlalchemy import create_engine
engine = create_engine('postgresql://admin:admin@127.0.0.1:5434/app_db')
df = pd.read_sql('SELECT * FROM "Enroll" LIMIT 1', engine)
print(df.columns.tolist())
