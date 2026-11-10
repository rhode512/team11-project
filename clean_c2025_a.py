from pathlib import Path
import numpy as np
import pandas as pd

# Resolve input and output paths relative to the project root.
PROJECT_DIR = Path(__file__).resolve().parent
RAW_CSV_PATH = PROJECT_DIR / 'data' / 'c2025_a.csv'
CLEANED_CSV_PATH = PROJECT_DIR / 'c2025_a_cleaned.csv'

if not RAW_CSV_PATH.exists():
    raise FileNotFoundError(
        f"Raw CSV file not found at: {RAW_CSV_PATH}\n"
        "Make sure 'c2025_a.csv' is in the project's data folder."
    )

print(f'Reading raw completions data from: {RAW_CSV_PATH.name}...')
df = pd.read_csv(RAW_CSV_PATH, low_memory=False, on_bad_lines='skip')

# Standardize missing value indicators
df.replace(['PrivacySuppressed', 'NULL', 'None', 'nan', 'NaN'], np.nan, inplace=True)

# Format primary key UNITID
df['UNITID'] = pd.to_numeric(df['UNITID'], errors='coerce')
df_clean = df.dropna(subset=['UNITID']).copy()
df_clean['UNITID'] = df_clean['UNITID'].astype(int)

# Export cleaned file preserving original file name convention [OriginalName]_cleaned.csv
df_clean.to_csv(CLEANED_CSV_PATH, index=False)
print(
    f'Successfully created {CLEANED_CSV_PATH.name} with {len(df_clean):,} records!'
)