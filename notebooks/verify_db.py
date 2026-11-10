import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://team11:change_me@127.0.0.1:3306/team11")
tables = pd.read_sql("SHOW TABLES;", engine)

print("\n=== DATABASE TABLES & ROW COUNTS ===")
for table in tables.iloc[:, 0]:
    count = pd.read_sql(f"SELECT COUNT(*) as cnt FROM `{table}`", engine).iloc[0]["cnt"]
    print(f"- {table}: {count:,} rows")