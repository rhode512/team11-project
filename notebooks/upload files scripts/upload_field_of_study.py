import os
from pathlib import Path
import pandas as pd
import sqlalchemy as sa

# Determine root directory (2 levels up from 'upload files scripts')
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
CLEANED_CSV_PATH = (
    PROJECT_ROOT / 'Most-Recent-Cohorts-Field-of-Study_cleaned.csv'
)

if not CLEANED_CSV_PATH.exists():
  raise FileNotFoundError(
      f"Cleaned CSV file not found at: {CLEANED_CSV_PATH}\nMake sure"
      " 'Most-Recent-Cohorts-Field-of-Study_cleaned.csv' is in your root project"
      ' folder.'
  )

# Connection string for local MySQL root user (no password)
SERVER_URI = os.getenv(
    'MYSQL_ROOT_URL', 'mysql+pymysql://root@127.0.0.1:3306'
)

# 1. Create database 'team11' if it does not exist
server_engine = sa.create_engine(SERVER_URI, pool_pre_ping=True)
with server_engine.connect() as conn:
  conn.execute(sa.text('CREATE DATABASE IF NOT EXISTS team11;'))

# 2. Upload to 'field_of_study_stage' table in database 'team11'
db_engine = sa.create_engine(f'{SERVER_URI}/team11', pool_pre_ping=True)
print(f'Reading cleaned data from: {CLEANED_CSV_PATH.name}...')
df_clean = pd.read_csv(CLEANED_CSV_PATH)

df_clean.to_sql(
    name='field_of_study_stage',
    con=db_engine,
    if_exists='replace',
    index=False,
)

print(
    "Successfully created/updated table 'field_of_study_stage' in database"
    " 'team11'!"
)