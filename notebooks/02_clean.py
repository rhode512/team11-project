"""Steps 2.1-2.2: Pull raw tables, clean them, and load the keyed tables.

Run from the repo folder:  python notebooks/02_clean.py
Run sql/01_schema.sql and sql/02_views.sql first.
To start over: rerun both SQL files, then this script.
"""
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://team11:change_me@localhost:3306/team11"
)

# Same names as in 01_load_raw.py
FOS_EARN_COL = "EARN_MDN_4YR"
FOS_DEBT_COL = "DEBT_ALL_STGP_EVAL_MDN"
CARNEGIE_COL = "C21BASIC"


def to_num(df, cols):
    """Convert text to numbers; 'PrivacySuppressed' and 'NULL' become NaN."""
    for col in cols:
        before = df[col].isna().sum()
        df[col] = pd.to_numeric(df[col], errors="coerce")
        print(f"  {col}: {df[col].isna().sum() - before} values became NaN")
    return df


# ---- 2.1 Pull the raw tables ----
print(pd.read_sql("SELECT COUNT(*) AS n FROM raw_hd", engine))

hd = pd.read_sql("SELECT * FROM raw_hd WHERE STABBR = 'TX'", engine)
cip = pd.read_sql("SELECT * FROM raw_cip", engine)
sc = pd.read_sql("SELECT * FROM raw_scorecard", engine)
fos = pd.read_sql("SELECT * FROM raw_fos", engine)
comp = pd.read_sql("SELECT * FROM raw_completions", engine)

# ---- 2.2 Clean ----

# institution: Texas schools from IPEDS
print("institution")
hd = hd.rename(columns={"UNITID": "unitid", "INSTNM": "instnm",
                        "STABBR": "stabbr", "CONTROL": "control",
                        "ICLEVEL": "iclevel", CARNEGIE_COL: "carnegie"})
hd = to_num(hd, ["unitid", "control", "iclevel", "carnegie"])
tx_ids = set(hd["unitid"])

# cip_family: two-digit families with readable names
cip["CIPCode"] = (cip["CIPCode"]
                  .str.replace(r'[="]', "", regex=True).str.strip())
fam = cip[cip["CIPCode"].str.len() == 2]
cip_family = pd.DataFrame({
    "cip2": fam["CIPCode"],
    "family_name": fam["CIPTitle"].str.rstrip(".").str.title(),
})

# scorecard_outcomes: Texas schools only, suppressed values -> NaN
print("scorecard_outcomes")
sc.columns = sc.columns.str.lower()
sc = sc.rename(columns={"pctpell": "pct_pell"})
sc["unitid"] = pd.to_numeric(sc["unitid"], errors="coerce")
sc = sc[sc["unitid"].isin(tx_ids)].copy()
sc = to_num(sc, [c for c in sc.columns if c != "unitid"])

# field_outcomes: fix CIP codes, numbers, and duplicate keys
print("field_outcomes")
fos = fos.rename(columns={"UNITID": "unitid", "CIPCODE": "cipcode",
                          "CREDLEV": "credlev", "IPEDSCOUNT2": "n_awards",
                          FOS_EARN_COL: "earn_mdn", FOS_DEBT_COL: "debt_mdn"})
fos["unitid"] = pd.to_numeric(fos["unitid"], errors="coerce")
fos = fos[fos["unitid"].isin(tx_ids)].copy()
fos["cipcode"] = fos["cipcode"].str.strip().str.zfill(4)   # 101 -> 0101
fos["cip2"] = fos["cipcode"].str[:2]
fos = to_num(fos, ["credlev", "n_awards", "earn_mdn", "debt_mdn"])

key = ["unitid", "cipcode", "credlev"]
print("  duplicate field rows:", fos.duplicated(key).sum())
fos = fos.sort_values("n_awards", ascending=False).drop_duplicates(key)
fos = fos[fos["cip2"].isin(cip_family["cip2"])]

# completions: drop totals and second majors, fix CIP codes
print("completions")
comp.columns = comp.columns.str.lower()
comp["unitid"] = pd.to_numeric(comp["unitid"], errors="coerce")
comp = comp[comp["unitid"].isin(tx_ids)].copy()
comp = to_num(comp, ["majornum", "awlevel", "ctotalt"])
comp["cipcode"] = comp["cipcode"].str.strip()
comp = comp[~comp["cipcode"].str.startswith("99")
            & (comp["majornum"] == 1)]
comp["cipcode"] = comp["cipcode"].str.zfill(7)             # 1.0101 -> 01.0101
comp["cip2"] = comp["cipcode"].str[:2]
comp = comp[comp["cip2"].isin(cip_family["cip2"])]

# ---- Load into the keyed tables, parents first ----
for name, df in [("institution", hd), ("cip_family", cip_family),
                 ("scorecard_outcomes", sc), ("field_outcomes", fos),
                 ("completions", comp)]:
    df.to_sql(name, engine, if_exists="append", index=False)
    print(f"loaded {name}: {len(df):,} rows")

# ---- Log Texas public four-years left out of the analysis ----
excluded = pd.read_sql("""
    SELECT i.unitid, i.instnm, s.npt41_pub, s.pell_debt_mdn,
           s.md_earn_wne_p10
    FROM institution i
    LEFT JOIN scorecard_outcomes s ON i.unitid = s.unitid
    WHERE i.control = 1 AND i.iclevel = 1
      AND (s.unitid IS NULL OR s.npt41_pub IS NULL
           OR s.md_earn_wne_p10 IS NULL)
""", engine)
excluded.to_csv("excluded_universities.csv", index=False)
print(f"{len(excluded)} universities excluded")
print(pd.read_sql("SELECT COUNT(*) AS n FROM tx_public_4yr", engine))
