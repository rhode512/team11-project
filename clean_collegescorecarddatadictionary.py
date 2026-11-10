from pathlib import Path
import numpy as np
import pandas as pd

# Resolve input and output paths relative to the project root.
PROJECT_DIR = Path(__file__).resolve().parent
RAW_EXCEL_PATH = (
    PROJECT_DIR / 'data' / 'CollegeScorecardDataDictionary.xlsx'
)
CLEANED_CSV_PATH = PROJECT_DIR / 'CollegeScorecardDataDictionary_cleaned.csv'

if not RAW_EXCEL_PATH.exists():
    raise FileNotFoundError(
        f"Raw Excel file not found at: {RAW_EXCEL_PATH}\n"
        "Make sure the workbook is in the project's data folder."
    )

print(f'Reading raw data dictionary from: {RAW_EXCEL_PATH.name}...')

# Read institution data dictionary tab
df = pd.read_excel(
    RAW_EXCEL_PATH, sheet_name='Institution_Data_Dictionary', engine='openpyxl'
)

# Standardize missing value indicators
df.replace(['PrivacySuppressed', 'NULL', 'None', 'nan', 'NaN'], np.nan, inplace=True)

# Clean column headers
df.columns = [str(c).strip() for c in df.columns]

# Export cleaned CSV preserving original file name convention [OriginalName]_cleaned.csv
df.to_csv(CLEANED_CSV_PATH, index=False)
print(
    f'Successfully created {CLEANED_CSV_PATH.name} with {len(df):,} records!'
)