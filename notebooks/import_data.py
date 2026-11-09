import os
import pandas as pd
from sqlalchemy import create_engine

# Database Connection Setup
DB_USER = "team11"
DB_PASS = "change_me"
DB_HOST = "127.0.0.1"
DB_PORT = "3306"
DB_NAME = "team11"

# Create SQLAlchemy connection engine
db_url = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(db_url)

# Define path to raw data file
# Adjust file name to match your dataset in the data/ folder
data_file_path = os.path.join("..", "data", "your_dataset.csv") 

def load_data_to_mariadb(file_path, table_name):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found. Make sure it is placed in the 'data/' directory.")
        return

    print(f"Reading {file_path}...")
    df = pd.read_csv(file_path)
    
    # Clean column names (replace spaces/special characters with underscores)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('[^a-zA-Z0-9_]', '', regex=True)

    print(f"Loading {len(df)} rows into table '{table_name}'...")
    
    # Stream data into MariaDB (creates table automatically if it doesn't exist)
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="replace",  # Options: 'fail', 'replace', or 'append'
        index=False,
        chunksize=5000         # Writes in batches for higher performance
    )
    
    print(f"✅ Successfully loaded '{table_name}' into MariaDB!")

if __name__ == "__main__":
    # Replace 'my_table_name' with your desired MariaDB table name
    load_data_to_mariadb(data_file_path, table_name="raw_project_data")