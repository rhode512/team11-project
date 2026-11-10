"""Steps 2.3-2.5: Compute metrics and save results.csv for the charts.

Run from the repo folder:  python notebooks/03_metrics.py
"""
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://team11:change_me@localhost:3306/team11"
)

FLAG_THRESHOLD = -0.10   # agreed in Phase 4; -0.10 = 10% below expected
MIN_COVERAGE = 0.60      # need earnings data for at least 60% of degrees

inst = pd.read_sql("SELECT * FROM tx_public_4yr", engine)
mix = pd.read_sql("SELECT * FROM program_mix", engine)
fe = pd.read_sql("SELECT * FROM field_earnings", engine)

# ---- 2.3 Return on cost ----
# Earnings vs. four years of net price for $0-30k families
inst["roi_cost"] = inst["md_earn_wne_p10"] / (4 * inst["npt41_pub"])
# Earnings vs. median debt for Pell recipients
inst["roi_debt"] = inst["md_earn_wne_p10"] / inst["pell_debt_mdn"]

# ---- 2.4 Program mix, expected and actual earnings, gap ----
# Statewide median earnings for each field family
state = (fe.groupby("cip2")["uni_field_earn"].median()
         .rename("state_field_earn").reset_index())

# Combine each school's mix with its own and statewide field earnings
m = (mix.merge(fe, on=["unitid", "cip2"], how="left")
        .merge(state, on="cip2", how="left"))
m = m.dropna(subset=["uni_field_earn", "state_field_earn"])

# Re-weight shares across the fields that have earnings data
m["weight"] = m["degrees"] / m.groupby("unitid")["degrees"].transform("sum")
m["expected_part"] = m["weight"] * m["state_field_earn"]
m["actual_part"] = m["weight"] * m["uni_field_earn"]

summary = (m.groupby("unitid")
           .agg(expected=("expected_part", "sum"),
                actual=("actual_part", "sum"),
                covered_degrees=("degrees", "sum"))
           .reset_index())

# Coverage: share of each school's degrees that had earnings data
total = mix.groupby("unitid")["degrees"].sum().rename("total_degrees")
summary = summary.merge(total, on="unitid")
summary["coverage"] = summary["covered_degrees"] / summary["total_degrees"]

# Gap, and the part explained by program mix
summary["gap"] = summary["actual"] - summary["expected"]
summary["gap_pct"] = summary["gap"] / summary["expected"]
results = inst.merge(summary, on="unitid", how="left")
results["mix_gap"] = results["expected"] - results["expected"].median()

# ---- 2.5 Flag and save ----
results["flagged"] = ((results["gap_pct"] <= FLAG_THRESHOLD)
                      & (results["coverage"] >= MIN_COVERAGE))

results.to_csv("results.csv", index=False)       # one row per university
m.to_csv("field_detail.csv", index=False)        # one row per school x field

print(results[["instnm", "roi_cost", "expected", "actual", "gap_pct",
               "flagged"]].sort_values("gap_pct").to_string())
