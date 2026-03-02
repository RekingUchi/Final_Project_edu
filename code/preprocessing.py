import requests
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import os
import glob
from pathlib import Path
# ════════════════════════════════════════════════
# PART 1: CPS Data Cleaning
# ════════════════════════════════════════════════

# ── load in data─────────────────────────────────
# Look for CPS data file in data/raw-data directory

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DERIVED_DATA_DIR = PROJECT_ROOT / "data" / "raw-data"
cps_file_path = DERIVED_DATA_DIR / "CPS_data.csv"
df_cps = pd.read_csv(cps_file_path)

for col in df_cps.columns:
    print(col)

# filter out the variables needed
cols = [
    "School_ID", "Long_Name", "Primary_Category",
    "School_Latitude", "School_Longitude",
    "Graduation_4_Year_School_Pct_Year_2",
    "College_Enrollment_School_Pct_Year_2",
    "SAT_Grade_11_Score_School_Avg"
]

df_hs = df_cps[df_cps["Primary_Category"] == "HS"][cols].copy()
df_hs = df_hs.dropna(subset=["Graduation_4_Year_School_Pct_Year_2", "College_Enrollment_School_Pct_Year_2"])
df_hs["Transition_Gap"] = df_hs["Graduation_4_Year_School_Pct_Year_2"] - df_hs["College_Enrollment_School_Pct_Year_2"]

print(len(df_hs))

# Save cleaned CPS data to derived-data directory
derived_data_dir = "../data/derived-data"
os.makedirs(derived_data_dir, exist_ok=True)

cps_clean_path = os.path.join(derived_data_dir, "CPS_clean_data.csv")
df_hs.to_csv(cps_clean_path, index=False)
print(f"Saved cleaned CPS data to: {cps_clean_path}")

# ════════════════════════════════════════════════
# PART 2: ACS Data Download
# ════════════════════════════════════════════════

API_KEY  = "ef9b79a5ab62a54bb237c8b342a7bf5e5a1c502b"
BASE_URL = "https://api.census.gov/data/2024/acs/acs5"
STATE    = "17"       # Illinois
COUNTY   = "031"      # Cook County

variables = [
    # poverty
    "B17001_001E", "B17001_002E",
    # income
    "B19013_001E",
    # labor force / unemployment
    "B23025_003E", "B23025_005E",
    # single-parent households
    "B11004_001E", "B11004_010E", "B11004_016E",
    # rent burden
    "B25070_001E", "B25070_007E", "B25070_008E", "B25070_009E", "B25070_010E",
]

url = (
    f"{BASE_URL}"
    f"?get=NAME,{','.join(variables)}"
    f"&for=tract:*"
    f"&in=state:{STATE}%20county:{COUNTY}"
    f"&key={API_KEY}"
)

print("Fetching data from Census API (Cook County Census Tracts)...")
response = requests.get(url)

if response.status_code != 200:
    print(f"Request failed, status code: {response.status_code}")
    print(response.text)
    exit()

print("Data fetched successfully. Processing...")

data = response.json()
df = pd.DataFrame(data[1:], columns=data[0])

df[variables] = df[variables].apply(pd.to_numeric, errors="coerce")

# 1. Poverty rate
df["poverty_rate"] = df["B17001_002E"] / df["B17001_001E"]

# 2. Log median income
df["log_median_income"] = np.where(
    df["B19013_001E"] > 0,
    np.log(df["B19013_001E"]),
    np.nan
)

# 3. Unemployment rate
df["unemployment_rate"] = df["B23025_005E"] / df["B23025_003E"]

# 4. Single-parent household rate
df["single_parent_rate"] = (
    df["B11004_010E"] + df["B11004_016E"]
) / df["B11004_001E"]

# 5. Rent burden rate (rent >= 30% of income)
df["rent_burden_rate"] = (
    df[["B25070_007E", "B25070_008E", "B25070_009E", "B25070_010E"]].sum(axis=1)
    / df["B25070_001E"]
)

df["GEOID"] = df["state"] + df["county"] + df["tract"]

clean_cols = [
    "GEOID", "NAME",
    "poverty_rate", "log_median_income", "unemployment_rate",
    "single_parent_rate", "rent_burden_rate"
]
df_clean = df[clean_cols].copy()

n_before = len(df_clean)
df_clean = df_clean.dropna()
n_after = len(df_clean)

# Save ACS data to derived-data directory
acs_raw_path = os.path.join(derived_data_dir, "acs_raw_chicago.csv")
acs_clean_path = os.path.join(derived_data_dir, "acs_clean_chicago.csv")

df.to_csv(acs_raw_path, index=False)
df_clean.to_csv(acs_clean_path, index=False)
print(f"Saved raw ACS data to: {acs_raw_path}")
print(f"Saved cleaned ACS data to: {acs_clean_path}")

print(f"\nDone!")
print(f"Total Census Tracts: {n_before}")
print(f"Remaining after dropping missing values: {n_after}")
print("\nFirst 5 rows:")
print(df_clean.head())
print("\nDescriptive statistics:")
print(df_clean.drop(columns=["GEOID", "NAME"]).describe().round(3))

# ════════════════════════════════════════════════
# PART 3: ACS Data Cleaning & PCA
# ════════════════════════════════════════════════

# ── load in data─────────────────────────────────
# Load ACS data from derived-data directory
acs_clean_path = os.path.join(derived_data_dir, "acs_clean_chicago.csv")
acs_raw_path = os.path.join(derived_data_dir, "acs_raw_chicago.csv")

print(f"Loading ACS cleaned data from: {acs_clean_path}")
print(f"Loading ACS raw data from: {acs_raw_path}")

df_clean = pd.read_csv(acs_clean_path)
df_raw   = pd.read_csv(acs_raw_path)

df_clean["GEOID"] = df_clean["GEOID"].astype(str)
df_raw["GEOID"]   = df_raw["GEOID"].astype(str)

df_clean["population"] = df_raw.set_index("GEOID")["B17001_001E"].reindex(df_clean["GEOID"]).values

df_clean = df_clean[df_clean["population"] > 100]
df_clean = df_clean[df_clean["unemployment_rate"] > 0]

print(f"Remaining tracts after cleaning: {len(df_clean)}")

pca_vars = [
    "poverty_rate",
    "log_median_income",
    "unemployment_rate",
    "single_parent_rate",
    "rent_burden_rate"
]

print("\n=== Variable Correlation Matrix ===")
print(df_clean[pca_vars].corr().round(2))

X = df_clean[pca_vars].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

pca = PCA()
pca.fit(X_scaled)

print("\n=== Explained Variance by Principal Component ===")
for i, var in enumerate(pca.explained_variance_ratio_):
    print(f"  PC{i+1}: {var:.3f}  (Cumulative: {pca.explained_variance_ratio_[:i+1].sum():.3f})")

plt.figure(figsize=(6, 4))
plt.plot(range(1, len(pca_vars) + 1), pca.explained_variance_ratio_, 'o-', color="#2E75B6", linewidth=2, markersize=7)
plt.title("Scree Plot", fontsize=14)
plt.xlabel("Principal Component", fontsize=12)
plt.ylabel("Variance Explained", fontsize=12)
plt.xticks(range(1, len(pca_vars) + 1))
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()
# Save scree plot to derived-data directory
scree_plot_path = os.path.join(derived_data_dir, "scree_plot.png")
plt.savefig(scree_plot_path, dpi=150)
print(f"Scree plot saved to: {scree_plot_path}")
plt.show()


print("\n=== Factor Loadings for PC1 ===")
loadings = pd.Series(pca.components_[0], index=pca_vars)
print(loadings.round(3))

scores = pca.transform(X_scaled)[:, 0]
if loadings["poverty_rate"] < 0:
    print("\nWarning: poverty_rate loading is negative. Flipping PC1 direction...")
    scores = -scores

df_clean["disadvantage_score"] = scores

print("\n=== Disadvantage Score Descriptive Statistics ===")
print(df_clean["disadvantage_score"].describe().round(3))

print("\n=== Top 10 Most Disadvantaged Tracts ===")
print(df_clean[["GEOID", "NAME", "disadvantage_score"]].sort_values(
    "disadvantage_score", ascending=False).head(10).to_string(index=False))

print("\n=== Top 10 Least Disadvantaged Tracts ===")
print(df_clean[["GEOID", "NAME", "disadvantage_score"]].sort_values(
    "disadvantage_score", ascending=True).head(10).to_string(index=False))

# Save PCA results to derived-data directory
acs_pca_path = os.path.join(derived_data_dir, "acs_with_pca_score.csv")
df_clean.drop(columns=["population"]).to_csv(acs_pca_path, index=False)
print(f"\nResults saved to: {acs_pca_path}")
