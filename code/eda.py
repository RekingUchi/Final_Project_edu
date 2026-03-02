# eda.py
#
# Basic data quality checks and non-spatial EDA
# using the school-level dataset with neighborhood disadvantage index.

from pathlib import Path

import pandas as pd

# ---------- Paths ----------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DERIVED_DATA_DIR = PROJECT_ROOT / "data" / "derived-data"

SCHOOLS_PATH = DERIVED_DATA_DIR / "schools_with_ndi.csv"


# ---------- Main script ----------

# 1. Load data
print(f"Reading school-level data from: {SCHOOLS_PATH}")
schools = pd.read_csv(SCHOOLS_PATH)

print("\n=== Basic info ===")
print("Shape:", schools.shape)
print("Column names:")
print(schools.columns.tolist())

# If geometry got saved as a column in the CSV, drop it for non-spatial EDA
if "geometry" in schools.columns:
    schools = schools.drop(columns=["geometry"])

print("\n=== First 5 rows ===")
print(schools.head())


# 2. Missing values

print("\n=== Missing values by column (only non-zero shown) ===")
missing = schools.isna().sum()
missing_nonzero = missing[missing > 0]
if missing_nonzero.empty:
    print("No missing values detected in this dataset.")
else:
    print(missing_nonzero)


# 3. Summary statistics for key numeric variables

numeric_candidates = [
    "Graduation_4_Year_School_Pct_Year_2",
    "College_Enrollment_School_Pct_Year_2",
    "SAT_Grade_11_Score_School_Avg",
    "Transition_Gap",
    "disadvantage_score",
    "poverty_rate",
    "log_median_income",
    "unemployment_rate",
    "single_parent_rate",
    "rent_burden_rate",
]

numeric_cols = [c for c in numeric_candidates if c in schools.columns]

print("\n=== Numeric columns used in summary stats ===")
print(numeric_cols)

if numeric_cols:
    print(
        "\n=== Summary stats for key numeric variables "
        "(including selected percentiles) ==="
    )
    summary = schools[numeric_cols].describe(
        percentiles=[0.1, 0.25, 0.5, 0.75, 0.9]
    )
    print(summary)
    # Optionally save to a CSV for later reference
    summary_out = DERIVED_DATA_DIR / "eda_numeric_summary.csv"
    summary.to_csv(summary_out)
    print(f"\nSaved numeric summary table to: {summary_out}")
else:
    print("\nNo numeric columns found for summary statistics.")


# 4. Outcomes by neighborhood disadvantage quintile

if "disadvantage_score" in schools.columns:
    print(
        "\n=== Outcomes by neighborhood disadvantage quintile "
        "(1 = least disadvantaged, 5 = most disadvantaged) ==="
    )

    # Drop rows without disadvantage_score
    df = schools.dropna(subset=["disadvantage_score"]).copy()

    try:
        df["ndi_quintile"] = pd.qcut(
            df["disadvantage_score"],
            5,
            labels=[1, 2, 3, 4, 5],
        )
    except ValueError as e:
        print("Could not compute quintiles for disadvantage_score:")
        print(e)
        ndi_quintile_table = None
    else:
        outcome_candidates = [
            "Graduation_4_Year_School_Pct_Year_2",
            "College_Enrollment_School_Pct_Year_2",
            "Transition_Gap",
        ]
        outcome_cols = [c for c in outcome_candidates if c in df.columns]

        if outcome_cols:
            ndi_quintile_table = (
                df.groupby("ndi_quintile")[outcome_cols].mean()
            )
            print(ndi_quintile_table)

            # Save this table for later plotting / report
            quintile_out = (
                DERIVED_DATA_DIR / "eda_outcomes_by_ndi_quintile.csv"
            )
            ndi_quintile_table.to_csv(quintile_out)
            print(f"\nSaved quintile summary table to: {quintile_out}")
        else:
            print("No outcome columns found for quintile summary.")
else:
    print(
        "\nColumn 'disadvantage_score' not found; "
        "cannot compute quintile-based EDA."
    )


# 5. (Optional) quick look at school types

if "Primary_Category" in schools.columns:
    print("\n=== School type counts (Primary_Category) ===")
    print(schools["Primary_Category"].value_counts())
