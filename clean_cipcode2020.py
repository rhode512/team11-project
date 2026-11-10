from pathlib import Path
import numpy as np
import pandas as pd

# Resolve input and output paths relative to the project root.
PROJECT_DIR = Path(__file__).resolve().parent
RAW_CSV_PATH = PROJECT_DIR / 'data' / 'CIPCode2020.csv'
CLEANED_CSV_PATH = PROJECT_DIR / 'CIPCode2020_cleaned.csv'

if not RAW_CSV_PATH.exists():
    raise FileNotFoundError(
        f"Raw CSV file not found at: {RAW_CSV_PATH}\n"
        "Make sure 'CIPCode2020.csv' is in the project's data folder."
    )

print(f'Reading raw data from: {RAW_CSV_PATH.name}...')
df = pd.read_csv(RAW_CSV_PATH, low_memory=False, on_bad_lines='skip')

# Strip Excel formula formatting (e.g., ='="01"' -> '01')
for col in df.columns:
  if df[col].dtype == object:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(r'^="?([^"]*)"?$', r'\1', regex=True)
    )

# Standardize missing value indicators
df.replace(['PrivacySuppressed', 'NULL', 'None', 'nan', 'NaN'], np.nan, inplace=True)

# Export cleaned file following standard naming convention [OriginalName]_cleaned.csv
df.to_csv(CLEANED_CSV_PATH, index=False)
print(
    f'Successfully created {CLEANED_CSV_PATH.name} with {len(df):,} records!'
)