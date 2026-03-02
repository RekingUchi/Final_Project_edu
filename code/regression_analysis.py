# regression_analysis.py
#
# Step 4: Regression analysis and visualization
# - Load school-level data with neighborhood disadvantage index
# - Run three regression models:
#   1. Graduation rate ~ disadvantage score
#   2. College enrollment rate ~ disadvantage score  
#   3. Transition gap ~ disadvantage score
# - Create scatter plots with regression lines
# - Save regression results and plots

from pathlib import Path
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns

# ---------- Paths ----------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DERIVED_DATA_DIR = PROJECT_ROOT / "data" / "derived-data"

SCHOOLS_PATH = DERIVED_DATA_DIR / "schools_with_ndi.csv"
OUTPUT_DIR = DERIVED_DATA_DIR

# ---------- Load data ----------

print(f"Reading school-level data from: {SCHOOLS_PATH}")
schools = pd.read_csv(SCHOOLS_PATH)

# If geometry column exists, drop it for regression analysis
if "geometry" in schools.columns:
    schools = schools.drop(columns=["geometry"])

print(f"\nDataset shape: {schools.shape}")
print(f"\nColumns: {schools.columns.tolist()}")

# Check for missing values in key variables
key_vars = ["Graduation_4_Year_School_Pct_Year_2", 
            "College_Enrollment_School_Pct_Year_2",
            "Transition_Gap", 
            "disadvantage_score"]

print("\n=== Missing values in key variables ===")
for var in key_vars:
    missing = schools[var].isna().sum()
    print(f"{var}: {missing} missing ({missing/len(schools)*100:.1f}%)")

# Remove rows with missing values in key variables for regression
schools_clean = schools.dropna(subset=key_vars).copy()
print(f"\nAfter removing missing values: {len(schools_clean)} schools remaining")

# ---------- Descriptive statistics ----------

print("\n=== Descriptive statistics ===")
desc_stats = schools_clean[key_vars].describe()
print(desc_stats)

# Save descriptive statistics
desc_stats.to_csv(OUTPUT_DIR / "regression_descriptive_stats.csv")
print(f"\nDescriptive statistics saved to: {OUTPUT_DIR / 'regression_descriptive_stats.csv'}")

# ---------- Regression functions ----------

def run_ols_regression(y, X, y_name, X_name):
    """Run OLS regression and return results"""
    # Add constant for intercept
    X_with_const = sm.add_constant(X)
    
    # Fit model
    model = sm.OLS(y, X_with_const)
    results = model.fit()
    
    # Print summary
    print(f"\n=== Regression: {y_name} ~ {X_name} ===")
    print(results.summary())
    
    # Extract key statistics
    coef = results.params[1]
    coef_se = results.bse[1]
    p_value = results.pvalues[1]
    r_squared = results.rsquared
    n_obs = results.nobs
    
    return {
        "y_name": y_name,
        "X_name": X_name,
        "coef": coef,
        "coef_se": coef_se,
        "p_value": p_value,
        "r_squared": r_squared,
        "n_obs": n_obs,
        "results": results
    }

# ---------- Run three regression models ----------

print("\n" + "="*60)
print("REGRESSION ANALYSIS")
print("="*60)

# Model 1: Graduation rate ~ disadvantage score
results1 = run_ols_regression(
    y=schools_clean["Graduation_4_Year_School_Pct_Year_2"],
    X=schools_clean["disadvantage_score"],
    y_name="Graduation Rate",
    X_name="Neighborhood Disadvantage Score"
)

# Model 2: College enrollment rate ~ disadvantage score
results2 = run_ols_regression(
    y=schools_clean["College_Enrollment_School_Pct_Year_2"],
    X=schools_clean["disadvantage_score"],
    y_name="College Enrollment Rate",
    X_name="Neighborhood Disadvantage Score"
)

# Model 3: Transition gap ~ disadvantage score
results3 = run_ols_regression(
    y=schools_clean["Transition_Gap"],
    X=schools_clean["disadvantage_score"],
    y_name="Transition Gap (Graduation - Enrollment)",
    X_name="Neighborhood Disadvantage Score"
)

# ---------- Compile regression results ----------

regression_results = pd.DataFrame([
    {
        "Model": "Graduation ~ Disadvantage",
        "Dependent Variable": "Graduation Rate (%)",
        "Independent Variable": "Disadvantage Score",
        "Coefficient": results1["coef"],
        "Std Error": results1["coef_se"],
        "P-value": results1["p_value"],
        "R-squared": results1["r_squared"],
        "N": results1["n_obs"]
    },
    {
        "Model": "Enrollment ~ Disadvantage",
        "Dependent Variable": "College Enrollment Rate (%)",
        "Independent Variable": "Disadvantage Score",
        "Coefficient": results2["coef"],
        "Std Error": results2["coef_se"],
        "P-value": results2["p_value"],
        "R-squared": results2["r_squared"],
        "N": results2["n_obs"]
    },
    {
        "Model": "Transition Gap ~ Disadvantage",
        "Dependent Variable": "Transition Gap (%)",
        "Independent Variable": "Disadvantage Score",
        "Coefficient": results3["coef"],
        "Std Error": results3["coef_se"],
        "P-value": results3["p_value"],
        "R-squared": results3["r_squared"],
        "N": results3["n_obs"]
    }
])

print("\n=== Summary of regression results ===")
print(regression_results.to_string(index=False))

# Save regression results
regression_results.to_csv(OUTPUT_DIR / "regression_results_summary.csv", index=False)
print(f"\nRegression results saved to: {OUTPUT_DIR / 'regression_results_summary.csv'}")

# ---------- Visualization ----------

print("\n" + "="*60)
print("CREATING VISUALIZATIONS")
print("="*60)

# Set style
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 11

# Create figure with 3 subplots
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Plot 1: Graduation rate vs disadvantage score
ax1 = axes[0]
sns.scatterplot(
    data=schools_clean,
    x="disadvantage_score",
    y="Graduation_4_Year_School_Pct_Year_2",
    alpha=0.6,
    edgecolor='w',
    linewidth=0.5,
    ax=ax1
)

# Add regression line
x_range = np.linspace(
    schools_clean["disadvantage_score"].min(),
    schools_clean["disadvantage_score"].max(),
    100
)
y_pred = results1["results"].params[0] + results1["results"].params[1] * x_range
ax1.plot(x_range, y_pred, color='red', linewidth=2, label='Regression line')

ax1.set_xlabel("Neighborhood Disadvantage Score")
ax1.set_ylabel("Graduation Rate (%)")
ax1.set_title("Graduation Rate vs Neighborhood Disadvantage")
ax1.legend()

# Add regression equation and R²
eq_text = f"y = {results1['coef']:.2f}x + {results1['results'].params[0]:.2f}\nR² = {results1['r_squared']:.3f}"
ax1.text(0.05, 0.95, eq_text, transform=ax1.transAxes, 
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# Plot 2: College enrollment rate vs disadvantage score
ax2 = axes[1]
sns.scatterplot(
    data=schools_clean,
    x="disadvantage_score",
    y="College_Enrollment_School_Pct_Year_2",
    alpha=0.6,
    edgecolor='w',
    linewidth=0.5,
    ax=ax2
)

# Add regression line
y_pred = results2["results"].params[0] + results2["results"].params[1] * x_range
ax2.plot(x_range, y_pred, color='red', linewidth=2, label='Regression line')

ax2.set_xlabel("Neighborhood Disadvantage Score")
ax2.set_ylabel("College Enrollment Rate (%)")
ax2.set_title("College Enrollment Rate vs Neighborhood Disadvantage")
ax2.legend()

# Add regression equation and R²
eq_text = f"y = {results2['coef']:.2f}x + {results2['results'].params[0]:.2f}\nR² = {results2['r_squared']:.3f}"
ax2.text(0.05, 0.95, eq_text, transform=ax2.transAxes, 
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# Plot 3: Transition gap vs disadvantage score
ax3 = axes[2]
sns.scatterplot(
    data=schools_clean,
    x="disadvantage_score",
    y="Transition_Gap",
    alpha=0.6,
    edgecolor='w',
    linewidth=0.5,
    ax=ax3
)

# Add regression line
y_pred = results3["results"].params[0] + results3["results"].params[1] * x_range
ax3.plot(x_range, y_pred, color='red', linewidth=2, label='Regression line')

ax3.set_xlabel("Neighborhood Disadvantage Score")
ax3.set_ylabel("Transition Gap (%)")
ax3.set_title("Transition Gap vs Neighborhood Disadvantage")
ax3.legend()

# Add regression equation and R²
eq_text = f"y = {results3['coef']:.2f}x + {results3['results'].params[0]:.2f}\nR² = {results3['r_squared']:.3f}"
ax3.text(0.05, 0.95, eq_text, transform=ax3.transAxes, 
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# Adjust layout and save
plt.tight_layout()
plot_path = OUTPUT_DIR / "regression_scatter_plots.png"
plt.savefig(plot_path, dpi=300, bbox_inches='tight')
print(f"\nScatter plots saved to: {plot_path}")

# ---------- Additional visualization: Coefficient plot ----------

fig2, ax = plt.subplots(figsize=(8, 5))

# Prepare data for coefficient plot
coef_data = pd.DataFrame({
    "Model": ["Graduation", "Enrollment", "Transition Gap"],
    "Coefficient": [results1["coef"], results2["coef"], results3["coef"]],
    "Std_Error": [results1["coef_se"], results2["coef_se"], results3["coef_se"]]
})

# Calculate confidence intervals
coef_data["CI_lower"] = coef_data["Coefficient"] - 1.96 * coef_data["Std_Error"]
coef_data["CI_upper"] = coef_data["Coefficient"] + 1.96 * coef_data["Std_Error"]

# Create coefficient plot
colors = ['skyblue', 'lightcoral', 'lightgreen']
for i, row in coef_data.iterrows():
    ax.errorbar(
        x=row["Coefficient"],
        y=row["Model"],
        xerr=[[row["Coefficient"] - row["CI_lower"]], [row["CI_upper"] - row["Coefficient"]]],
        fmt='o',
        color=colors[i],
        ecolor='black',
        capsize=5,
        markersize=8
    )

ax.axvline(x=0, color='gray', linestyle='--', alpha=0.7)
ax.set_xlabel("Regression Coefficient")
ax.set_title("Regression Coefficients: Impact of Neighborhood Disadvantage")
ax.grid(True, alpha=0.3)

# Add value labels
for i, row in coef_data.iterrows():
    ax.text(row["Coefficient"] + 0.05, i, f"{row['Coefficient']:.2f}", 
            verticalalignment='center', fontweight='bold')

plt.tight_layout()
coef_plot_path = OUTPUT_DIR / "regression_coefficients_plot.png"
plt.savefig(coef_plot_path, dpi=300, bbox_inches='tight')
print(f"Coefficient plot saved to: {coef_plot_path}")

# ---------- Summary of findings ----------

print("\n" + "="*60)
print("KEY FINDINGS")
print("="*60)

print("\n1. Graduation Rate vs Disadvantage:")
print(f"   Coefficient: {results1['coef']:.3f} (p-value: {results1['p_value']:.4f})")
if results1['p_value'] < 0.05:
    if results1['coef'] < 0:
        print("   ✓ Statistically significant negative relationship")
        print("   ✓ Higher disadvantage associated with lower graduation rates")
    else:
        print("   ✓ Statistically significant positive relationship")
else:
    print("   ✗ Not statistically significant")

print("\n2. College Enrollment Rate vs Disadvantage:")
print(f"   Coefficient: {results2['coef']:.3f} (p-value: {results2['p_value']:.4f})")
if results2['p_value'] < 0.05:
    if results2['coef'] < 0:
        print("   ✓ Statistically significant negative relationship")
        print("   ✓ Higher disadvantage associated with lower college enrollment")
    else:
        print("   ✓ Statistically significant positive relationship")
else:
    print("   ✗ Not statistically significant")

print("\n3. Transition Gap vs Disadvantage:")
print(f"   Coefficient: {results3['coef']:.3f} (p-value: {results3['p_value']:.4f})")
if results3['p_value'] < 0.05:
    if results3['coef'] > 0:
        print("   ✓ Statistically significant positive relationship")
        print("   ✓ Higher disadvantage associated with larger transition gaps")
        print("   ✓ This supports the hypothesis that neighborhood disadvantage")
        print("     weakens the transition from high school to college")
    else:
        print("   ✓ Statistically significant negative relationship")
else:
    print("   ✗ Not statistically significant")

print("\n" + "="*60)
print("ANALYSIS COMPLETE")
print("="*60)