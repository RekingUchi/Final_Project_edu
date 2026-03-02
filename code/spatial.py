# spatial.py
#
# Step 3: spatial join + prepare data for subsequent spatial analysis
# - Read CPS school data (with coordinates + outcomes)
# - Read ACS neighborhood disadvantage index (tract level)
# - Read Chicago census tracts KML boundaries
# - Spatially join: school points → tract GEOID
# - Merge ACS disadvantage_score onto schools
# - Create tract-level NDI layer for choropleth maps

from pathlib import Path

import pandas as pd
import geopandas as gpd

# ---------- Path settings ----------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DERIVED_DATA_DIR = PROJECT_ROOT / "data" / "derived-data"
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw-data"

CPS_PATH = DERIVED_DATA_DIR / "CPS_clean_data.csv"
ACS_PATH = DERIVED_DATA_DIR / "acs_with_pca_score.csv"

# This follows our naming convention: data/raw-data/chicago_tracts_2010.kml
TRACT_PATH = RAW_DATA_DIR / "chicago_tracts_2010.kml"


# ---------- Load CPS / ACS ----------

def load_cps() -> pd.DataFrame:
    cps = pd.read_csv(CPS_PATH)

    print("=== CPS_clean_data (shape) ===", cps.shape)
    print("=== CPS_clean_data (head) ===")
    print(cps.head(), "\n")

    return cps


def load_acs() -> pd.DataFrame:
    acs = pd.read_csv(ACS_PATH)

    # Ensure GEOID is a string so it can be merged with tract boundaries
    acs["GEOID"] = acs["GEOID"].astype(str).str.zfill(11)

    print("=== acs_with_pca_score (shape) ===", acs.shape)
    print("=== acs_with_pca_score (head) ===")
    print(acs.head(), "\n")

    return acs


# ---------- Schools → point geometries ----------

def make_school_points(cps: pd.DataFrame) -> gpd.GeoDataFrame:
    required = {"School_Longitude", "School_Latitude"}
    if not required.issubset(cps.columns):
        raise ValueError(f"CPS data missing: {required - set(cps.columns)}")

    schools_gdf = gpd.GeoDataFrame(
        cps,
        geometry=gpd.points_from_xy(
            cps["School_Longitude"], cps["School_Latitude"]
        ),
        crs="EPSG:4326",  # WGS84, latitude/longitude
    )

    print("=== Schools GeoDataFrame (head) ===")
    print(
        schools_gdf[
            [
                "School_ID",
                "Long_Name",
                "Primary_Category",
                "School_Latitude",
                "School_Longitude",
                "geometry",
            ]
        ].head(),
        "\n",
    )

    return schools_gdf


# ---------- Load tract KML and prepare GEOID ----------

def load_tracts_from_kml() -> gpd.GeoDataFrame:
    """
    Read Chicago census tracts from a KML file and ensure a GEOID field exists.
    The 2010 tracts from the Chicago Data Portal typically include geoid/geoid10.
    """
    print(f"Reading tracts from: {TRACT_PATH}")
    tracts = gpd.read_file(TRACT_PATH, driver="KML")

    print("=== Raw tracts from KML (columns) ===")
    print(tracts.columns.tolist())
    print("=== Raw tracts (head) ===")
    print(tracts.head(), "\n")

    # Try to find the GEOID column from several common names
    possible_geoid_cols = ["GEOID", "geoid", "geoid10", "GEOID10"]
    geoid_col = None
    for col in possible_geoid_cols:
        if col in tracts.columns:
            geoid_col = col
            break

    if geoid_col is None:
        raise ValueError(
            "tract KML doesn't have GEOID"
        )

    # Standardize to a single GEOID field
    tracts["GEOID"] = tracts[geoid_col].astype(str).str.zfill(11)

    # Keep only necessary fields
    tracts = tracts[["GEOID", "geometry"]].copy()

    # KML is typically WGS84; set CRS explicitly just in case
    if tracts.crs is None:
        tracts.set_crs(epsg=4326, inplace=True)

    print("=== Tracts GeoDataFrame (after GEOID processing, head) ===")
    print(tracts.head(), "\n")

    return tracts


# ---------- Spatial join + merge ACS ----------

def spatial_join_schools_tracts(
    schools_gdf: gpd.GeoDataFrame, tracts_gdf: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """
    Match each school to the census tract it falls into (point-in-polygon),
    producing a school-level table with GEOID.
    """
    # Ensure both layers use the same CRS
    if schools_gdf.crs != tracts_gdf.crs:
        tracts_gdf = tracts_gdf.to_crs(schools_gdf.crs)

    joined = gpd.sjoin(
        schools_gdf,
        tracts_gdf[["GEOID", "geometry"]],
        how="left",
        predicate="within",
    )

    # sjoin adds an index_right column; drop it
    if "index_right" in joined.columns:
        joined = joined.drop(columns=["index_right"])

    print("=== Schools after spatial join (head) ===")
    print(joined[["School_ID", "Long_Name", "GEOID", "geometry"]].head(), "\n")

    missing_geo = joined["GEOID"].isna().sum()
    print(f"{missing_geo} schools has empty values\n")

    return joined


def merge_schools_with_acs(
    schools_with_geo: gpd.GeoDataFrame, acs: pd.DataFrame
) -> gpd.GeoDataFrame:
    """
    Attach ACS disadvantage index and related variables to each school.
    """
    merged = schools_with_geo.merge(acs, on="GEOID", how="left")

    print("=== Schools with ACS (head) ===")
    print(
        merged[
            [
                "School_ID",
                "Long_Name",
                "GEOID",
                "disadvantage_score",
                "poverty_rate",
                "log_median_income",
            ]
        ].head(),
        "\n",
    )

    missing_ndi = merged["disadvantage_score"].isna().sum()
    print(f"{missing_ndi} schools have missing disadvantage_score\n")

    return merged


def make_tracts_with_acs(
    tracts_gdf: gpd.GeoDataFrame, acs: pd.DataFrame
) -> gpd.GeoDataFrame:
    """
    Build a tract-level GeoDataFrame for choropleth maps:
    tracts + ACS disadvantage index.
    """
    tracts_with_acs = tracts_gdf.merge(acs, on="GEOID", how="left")

    print("=== Tracts with ACS (head) ===")
    print(
        tracts_with_acs[
            ["GEOID", "disadvantage_score", "poverty_rate", "log_median_income"]
        ].head(),
        "\n",
    )

    return tracts_with_acs


# ---------- Main workflow ----------

def main():
    # 1. Load CPS / ACS
    cps = load_cps()
    acs = load_acs()

    # 2. Convert schools to point geometries
    schools_gdf = make_school_points(cps)

    # 3. Load tract boundaries (KML)
    tracts_gdf = load_tracts_from_kml()

    # 4. Spatially join schools to tracts
    schools_with_geo = spatial_join_schools_tracts(schools_gdf, tracts_gdf)

    # 5. Merge ACS disadvantage index into school data
    schools_with_acs = merge_schools_with_acs(schools_with_geo, acs)

    # 6. Build tract-level NDI layer
    tracts_with_acs = make_tracts_with_acs(tracts_gdf, acs)

    # 7. Save outputs for later analysis / plots / dashboard
    schools_csv_out = DERIVED_DATA_DIR / "schools_with_ndi.csv"
    schools_gpkg_out = DERIVED_DATA_DIR / "schools_with_ndi.gpkg"
    tracts_gpkg_out = DERIVED_DATA_DIR / "tracts_with_ndi.gpkg"

    # School-level: save both csv and gpkg (for regression and point maps)
    schools_with_acs.to_csv(schools_csv_out, index=False)
    schools_with_acs.to_file(schools_gpkg_out, driver="GPKG")

    # Tract-level: save gpkg for choropleth maps
    tracts_with_acs.to_file(tracts_gpkg_out, driver="GPKG")

    print(f"save school data: {schools_csv_out}")
    print(f"save school point GeoPackage: {schools_gpkg_out}")
    print(f"save tract NDI GeoPackage: {tracts_gpkg_out}")


if __name__ == "__main__":
    main()
