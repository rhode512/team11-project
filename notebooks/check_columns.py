"""Check that each data file has the columns our scripts expect.

Run from the repo folder:  python notebooks/check_columns.py
"""
import pandas as pd

NEEDED = {
    "data/hd2025.csv": ["UNITID", "INSTNM", "STABBR", "CONTROL", "ICLEVEL",
                        "C21BASIC"],
    "data/Most-Recent-Cohorts-Institution.csv": [
        "UNITID", "PCTPELL", "NPT41_PUB", "PELL_DEBT_MDN", "GRAD_DEBT_MDN",
        "MD_EARN_WNE_P10", "MN_EARN_WNE_INC1_P10"],
    "data/Most-Recent-Cohorts-Field-of-Study.csv": [
        "UNITID", "CIPCODE", "CREDLEV", "IPEDSCOUNT2"],
    "data/c2025_a.csv": ["UNITID", "CIPCODE", "MAJORNUM", "AWLEVEL",
                         "CTOTALT"],
    "data/CIPCode2020.csv": ["CIPCode", "CIPTitle"],
}

for path, cols in NEEDED.items():
    header = list(pd.read_csv(path, nrows=0, encoding="latin-1").columns)
    missing = [c for c in cols if c not in header]
    status = "OK" if not missing else f"MISSING {missing}"
    print(f"{path}: {status}")

# Carnegie column in the IPEDS directory (name changes by year)
hd = pd.read_csv("data/hd2025.csv", nrows=0, encoding="latin-1")
print("\nCarnegie columns in hd2025:", [c for c in hd.columns if "BASIC" in c])

# Field-of-study earnings and debt column names (change between releases)
fos = pd.read_csv("data/Most-Recent-Cohorts-Field-of-Study.csv", nrows=0,
                  encoding="latin-1")
print("\nEarnings columns:", [c for c in fos.columns if "EARN" in c])
print("\nDebt columns:", [c for c in fos.columns if "DEBT" in c])
