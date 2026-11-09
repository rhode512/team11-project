"""Step 1.4: Load the raw CSV files into MariaDB staging tables (all text).

Run from the repo folder:  python notebooks/01_load_raw.py
Docker must be running (docker compose up -d).
"""
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://team11:change_me@localhost:3306/team11"
)

# Replace with the names printed by check_columns.py
FOS_EARN_COL = "EARN_MDN_4YR"
FOS_DEBT_COL = "DEBT_ALL_STGP_EVAL_MDN"
CARNEGIE_COL = "C21BASIC"

# (file, table name, columns to keep)
RAW_FILES = [
    ("data/hd2025.csv", "raw_hd",
     ["UNITID", "INSTNM", "STABBR", "CONTROL", "ICLEVEL", CARNEGIE_COL]),
    ("data/Most-Recent-Cohorts-Institution.csv", "raw_scorecard",
     ["UNITID", "PCTPELL", "NPT41_PUB", "PELL_DEBT_MDN", "GRAD_DEBT_MDN",
      "MD_EARN_WNE_P10", "MN_EARN_WNE_INC1_P10"]),
    ("data/Most-Recent-Cohorts-Field-of-Study.csv", "raw_fos",
     ["UNITID", "CIPCODE", "CREDLEV", "IPEDSCOUNT2",
      FOS_EARN_COL, FOS_DEBT_COL]),
    ("data/c2025_a.csv", "raw_completions",
     ["UNITID", "CIPCODE", "MAJORNUM", "AWLEVEL", "CTOTALT"]),
    ("data/CIPCode2020.csv", "raw_cip", ["CIPCode", "CIPTitle"]),
]


def clean_name(name):
    """Remove the hidden start-of-file marker (BOM) and stray spaces."""
    return name.replace("\ufeff", "").replace("ï»¿", "").strip()


for path, table, cols in RAW_FILES:
    df = pd.read_csv(path, usecols=lambda c: clean_name(c) in cols,
                     dtype=str, encoding="latin-1")
    df.columns = [clean_name(c) for c in df.columns]

    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"{path} is missing columns: {missing}")

    df.to_sql(table, engine, if_exists="replace", index=False,
              chunksize=10000)
    print(f"{table}: {len(df):,} rows x {len(df.columns)} columns")
