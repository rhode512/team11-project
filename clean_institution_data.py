from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
DATA_FILE = PROJECT_DIR / 'data' / 'Most-Recent-Cohorts-Institution.csv'
OUTPUT_FILE = PROJECT_DIR / 'Most-Recent-Cohorts-Institution_cleaned.csv'

SELECT_COLS = [
    'UNITID',
    'OPEID6',
    'INSTNM',
    'CITY',
    'STABBR',
    'ZIP',
    'CONTROL',
    'MAIN',
    'CURROPER',
    'ADM_RATE',
    'UGDS',
    'TUITIONFEE_IN',
    'TUITIONFEE_OUT',
    'MD_EARN_WNE_P10',
    'GRAD_DEBT_MDN',
]

# Load raw dataset
df = pd.read_csv(
    DATA_FILE,
    usecols=lambda c: c in SELECT_COLS,
    low_memory=False,
)

# Replace privacy masks with NaN
df.replace(['PrivacySuppressed', 'NULL', 'None', 'nan', 'NaN'], np.nan, inplace=True)

# Coerce numeric columns
NUMERIC_COLS = [
    'ADM_RATE',
    'UGDS',
    'TUITIONFEE_IN',
    'TUITIONFEE_OUT',
    'MD_EARN_WNE_P10',
    'GRAD_DEBT_MDN',
]
for col in NUMERIC_COLS:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Ensure ID formatting while preserving missing values
# Convert to nullable integer so privacy-suppressed IDs do not crash the script.
df['UNITID'] = pd.to_numeric(df['UNITID'], errors='coerce').astype('Int64')

# Keep operating institutions
df_clean = df[df['CURROPER'] == 1].copy()

# Save cleaned output using the original name + _cleaned
# Write beside the source CSV so the output is created in the project root.
df_clean.to_csv(OUTPUT_FILE, index=False)
print(f'Done! Created file: {OUTPUT_FILE.name}')