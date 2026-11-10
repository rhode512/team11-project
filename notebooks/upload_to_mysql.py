import os
from pathlib import Path

import pandas as pd
import sqlalchemy as sa

PROJECT_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = Path(
    os.getenv(
        'CSV_PATH', PROJECT_DIR / 'Most-Recent-Cohorts-Institution_cleaned.csv'
    )
)

# Set default connection strings to no-password for root
ROOT_URL = os.getenv('MYSQL_ROOT_URL', 'mysql+pymysql://root@127.0.0.1:3306')
DB_URL = os.getenv('MYSQL_URL', 'mysql+pymysql://root@127.0.0.1:3306/team11')

if not CSV_PATH.exists():
  raise FileNotFoundError(f'Cleaned CSV not found: {CSV_PATH}')

# Create database 'team11' if it does not exist
server_engine = sa.create_engine(ROOT_URL, pool_pre_ping=True)
with server_engine.connect() as conn:
  conn.execute(sa.text('CREATE DATABASE IF NOT EXISTS team11;'))

# Upload to team11 database
db_engine = sa.create_engine(DB_URL, pool_pre_ping=True)
df = pd.read_csv(CSV_PATH)
df.to_sql(
    name='institution_stage', con=db_engine, if_exists='replace', index=False
)

print(
    "Successfully created/updated table 'institution_stage' in database"
    " 'team11'!"
)