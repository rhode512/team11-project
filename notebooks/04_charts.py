"""Steps 3.1-3.2: Diagnostic and final charts, saved as PNGs.

Run from the repo folder:  python notebooks/04_charts.py
Run 03_metrics.py first.
"""
import pandas as pd
import matplotlib.pyplot as plt

HIGHLIGHT = "#b85c38"
MUTED = "#9aa5b1"

results = pd.read_csv("results.csv")
detail = pd.read_csv("field_detail.csv")

# ---- 3.1 Diagnostic charts ----
# Histograms: the spread of each key measure
cols = ["md_earn_wne_p10", "npt41_pub", "pell_debt_mdn", "gap_pct"]
results[cols].hist(bins=15, figsize=(10, 6))
plt.tight_layout()
plt.savefig("diag_histograms.png", dpi=200)
plt.close()

# Boxplots: outliers show as dots
results[["roi_cost", "roi_debt"]].plot(
    kind="box", subplots=True, figsize=(8, 4)
)
plt.tight_layout()
plt.savefig("diag_boxplots.png", dpi=200)
plt.close()

# ---- 3.2 Chart 1: Return on cost ranking ----
r = results.sort_values("roi_cost")
colors = [HIGHLIGHT if f else MUTED for f in r["flagged"]]

plt.figure(figsize=(8, 10))
plt.barh(r["instnm"], r["roi_cost"], color=colors)
plt.xlabel("10-year earnings ÷ 4 years of net price ($0–30k families)")
plt.title("Return on cost at Texas public universities")
plt.tight_layout()
plt.savefig("chart1_roi_ranking.png", dpi=200)
plt.close()

# ---- Chart 2: Expected vs. actual earnings ----
fig, ax = plt.subplots(figsize=(7, 7))
ax.scatter(results["expected"], results["actual"],
           c=[HIGHLIGHT if f else MUTED for f in results["flagged"]])

lo = results[["expected", "actual"]].min().min()
hi = results[["expected", "actual"]].max().max()
ax.plot([lo, hi], [lo, hi], linestyle="--", color="gray")

for _, row in results[results["flagged"]].iterrows():
    ax.annotate(row["instnm"], (row["expected"], row["actual"]),
                fontsize=8, xytext=(4, -4), textcoords="offset points")

ax.set_xlabel("Expected earnings (from program mix)")
ax.set_ylabel("Actual earnings in the same fields")
ax.set_title("Which universities underperform their program mix?")
plt.tight_layout()
plt.savefig("chart2_expected_vs_actual.png", dpi=200)
plt.close()

# ---- Chart 3: Program mix at flagged universities ----
flagged_ids = results.loc[results["flagged"], "unitid"]
if len(flagged_ids) > 0:
    top = detail.groupby("family_name")["degrees"].sum().nlargest(6).index
    mm = detail[detail["unitid"].isin(flagged_ids)].copy()
    mm["family"] = mm["family_name"].where(mm["family_name"].isin(top),
                                           "Other")
    pivot = mm.pivot_table(index="unitid", columns="family",
                           values="weight", aggfunc="sum").fillna(0)
    pivot.index = pivot.index.map(results.set_index("unitid")["instnm"])

    pivot.plot(kind="barh", stacked=True, figsize=(9, 5))
    plt.xlabel("Share of bachelor's degrees")
    plt.title("Program mix at flagged universities")
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig("chart3_program_mix.png", dpi=200)
    plt.close()
else:
    print("No flagged universities, so Chart 3 was skipped.")

print("Charts saved.")
