import os
import pandas as pd
from sqlalchemy import create_engine

# Database Connection Setup
DB_USER = "team11"
DB_PASS = "change_me"
DB_HOST = "127.0.0.1"
DB_PORT = "3306"
DB_NAME = "team11"

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Your 6 project files
TARGET_FILES = [
    "c2025_a",
    "CIPCode2020",
    "CollegeScorecardDataDictionary",
    "hd2025",
    "Most-Recent-Cohorts-Field-of-Study",
    "Most-Recent-Cohorts-Institution"
]

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

def find_file_path(base_name):
    """Finds the actual file path regardless of extension (.csv, .xlsx, .xls)."""
    for ext in [".csv", ".xlsx", ".xls"]:
        path = os.path.join(DATA_DIR, base_name + ext)
        if os.path.exists(path):
            return path
    return None

def import_team11_datasets():
    print("Starting import for Team 11 datasets...\n")
    
    for base_name in TARGET_FILES:
        file_path = find_file_path(base_name)
        
        if not file_path:
            print(f"⚠️ Warning: Could not find '{base_name}' (.csv/.xlsx) in the data/ directory. Skipping...")
            continue
            
        # Clean table name for MariaDB (lowercase, hyphens/spaces to underscores)
        table_name = base_name.lower().replace("-", "_").replace(" ", "_")
        file_filename = os.path.basename(file_path)

        print(f"Reading {file_filename}...")
        
        # Read file into Pandas DataFrame based on file extension
        if file_path.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path, low_memory=False)

        # Standardize column names (lowercase, underscores, no special chars)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('[^a-zA-Z0-9_]', '', regex=True)

        print(f"Uploading {len(df):,} rows to table '{table_name}'...")
        
        # Write into MariaDB
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists="replace",
            index=False,
            chunksize=2000
        )
        print(f"✅ Successfully created table '{table_name}'.\n")

    print("🎉 All datasets imported successfully!")

if __name__ == "__main__":
    import_team11_datasets()