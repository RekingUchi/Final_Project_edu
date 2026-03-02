# plot_spatial.py
#
# Spatial analysis: create four maps
# 1) Choropleth of neighborhood disadvantage (tract level)
# 2) School points colored by graduation rate
# 3) School points colored by college enrollment
# 4) School points colored by transition gap

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt

# ---------- Paths ----------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DERIVED_DATA_DIR = PROJECT_ROOT / "data" / "derived-data"

TRACTS_PATH = DERIVED_DATA_DIR / "tracts_with_ndi.gpkg"
SCHOOLS_PATH = DERIVED_DATA_DIR / "schools_with_ndi.gpkg"

# ---------- Load data ----------

print(f"Reading tracts from: {TRACTS_PATH}")
tracts = gpd.read_file(TRACTS_PATH)

print(f"Reading schools from: {SCHOOLS_PATH}")
schools = gpd.read_file(SCHOOLS_PATH)

# Ensure both layers share the same CRS
if tracts.crs != schools.crs:
    schools = schools.to_crs(tracts.crs)

# Drop any rows without geometry just in case
tracts = tracts[tracts.geometry.notna()].copy()
schools = schools[schools.geometry.notna()].copy()


# ---------- Helper to make nice-looking plots ----------

def _base_ax(figsize=(8, 8)):
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    return fig, ax


# ---------- Map 1: Neighborhood disadvantage choropleth ----------

def plot_ndi_choropleth():
    fig, ax = _base_ax()

    tracts.plot(
        ax=ax,
        column="disadvantage_score",
        cmap="RdYlBu_r",
        linewidth=0.2,
        edgecolor="grey",
        legend=True,
        legend_kwds={"shrink": 0.7, "label": "Neighborhood Disadvantage Index"},
        missing_kwds={"color": "lightgrey", "hatch": "///", "label": "Missing"},
    )

    ax.set_axis_off()
    ax.set_title(
        "Neighborhood Disadvantage by Census Tract\nChicago, IL",
        fontsize=12,
    )
    fig.tight_layout()

    out_path = DERIVED_DATA_DIR / "map1_ndi_choropleth.png"
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Saved Map 1 (NDI choropleth) to: {out_path}")


# ---------- Shared base for point maps ----------

def _plot_school_points(
    value_col: str,
    title: str,
    out_filename: str,
    vmin=None,
    vmax=None,
):
    """
    Plot school points colored by a given column, with tract boundaries in the background.
    """
    fig, ax = _base_ax()

    # light tract boundaries as background
    tracts.boundary.plot(ax=ax, linewidth=0.3, color="lightgrey")

    # filter rows that have non-missing values for the chosen column
    df = schools.dropna(subset=[value_col]).copy()

    # point plot
    df.plot(
        ax=ax,
        column=value_col,
        cmap="viridis",
        markersize=35,
        legend=True,
        edgecolor="black",
        linewidth=0.1,
        vmin=vmin,
        vmax=vmax,
        legend_kwds={"shrink": 0.7, "label": value_col},
    )

    ax.set_axis_off()
    ax.set_title(title, fontsize=12)
    fig.tight_layout()

    out_path = DERIVED_DATA_DIR / out_filename
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Saved {title} to: {out_path}")


# ---------- Map 2: schools colored by graduation ----------

def plot_schools_by_graduation():
    col = "Graduation_4_Year_School_Pct_Year_2"
    _plot_school_points(
        value_col=col,
        title="Chicago High Schools\nColored by 4-Year Graduation Rate",
        out_filename="map2_schools_graduation.png",
        vmin=0,
        vmax=100,
    )


# ---------- Map 3: schools colored by college enrollment ----------

def plot_schools_by_enrollment():
    col = "College_Enrollment_School_Pct_Year_2"
    _plot_school_points(
        value_col=col,
        title="Chicago High Schools\nColored by College Enrollment Rate",
        out_filename="map3_schools_college_enrollment.png",
        vmin=0,
        vmax=100,
    )


# ---------- Map 4: schools colored by transition gap ----------

def plot_schools_by_transition_gap():
    col = "Transition_Gap"

    # For the gap we let vmin/vmax be from the data to show the full range
    vmin = schools[col].min()
    vmax = schools[col].max()

    _plot_school_points(
        value_col=col,
        title="Chicago High Schools\nColored by Graduation–Enrollment Gap",
        out_filename="map4_schools_transition_gap.png",
        vmin=vmin,
        vmax=vmax,
    )


# ---------- Main ----------

def main():
    plot_ndi_choropleth()
    plot_schools_by_graduation()
    plot_schools_by_enrollment()
    plot_schools_by_transition_gap()


if __name__ == "__main__":
    main()
