import os
from pathlib import Path
import pandas as pd
import sqlalchemy as sa

# Locate project root dynamically by searching upwards for the cleaned file
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR
while PROJECT_ROOT.parent != PROJECT_ROOT:
  if (PROJECT_ROOT / 'hd2025_cleaned.csv').exists():
    break
  PROJECT_ROOT = PROJECT_ROOT.parent

CLEANED_CSV_PATH = PROJECT_ROOT / 'hd2025_cleaned.csv'
TABLE_NAME = 'hd2025_stage'

if not CLEANED_CSV_PATH.exists():
  raise FileNotFoundError(
      f"Cleaned CSV file not found at: {CLEANED_CSV_PATH}\nMake sure"
      " 'hd2025_cleaned.csv' is in your root project folder."
  )

# Connection string for local MySQL root user (no password)
SERVER_URI = os.getenv(
    'MYSQL_ROOT_URL', 'mysql+pymysql://root@127.0.0.1:3306'
)

# 1. Ensure team11 database exists
server_engine = sa.create_engine(SERVER_URI, pool_pre_ping=True)
with server_engine.connect() as conn:
  conn.execute(sa.text('CREATE DATABASE IF NOT EXISTS team11;'))

# 2. Ingest cleaned CSV into hd2025_stage table
db_engine = sa.create_engine(f'{SERVER_URI}/team11', pool_pre_ping=True)
print(f'Reading cleaned dataset from: {CLEANED_CSV_PATH}...')
df_clean = pd.read_csv(CLEANED_CSV_PATH, low_memory=False)

df_clean.to_sql(
    name=TABLE_NAME,
    con=db_engine,
    if_exists='replace',
    index=False,
)

print(
    f"Successfully created/updated table '{TABLE_NAME}' in database 'team11'!"
)