# CPS School Analysis: Neighborhood Disadvantage and Educational Outcomes

## Project Overview

This project analyzes the relationship between neighborhood socioeconomic disadvantage and educational outcomes in Chicago Public Schools (CPS). The study examines how neighborhood characteristics affect graduation rates, college enrollment rates, and transition gaps between different student demographic groups.

## Research Questions

1. How does neighborhood socioeconomic disadvantage correlate with school-level graduation rates?
2. What is the relationship between neighborhood disadvantage and college enrollment rates?
3. How does neighborhood context affect the transition gap between different student groups?
4. Are there spatial patterns in educational outcomes across Chicago neighborhoods?

## Project Structure

```
final-project-yijia-ruilin-ruoyan/
├── README.md                    # This file
├── environment.yml              # Conda environment specification
├── .gitignore                   # Git ignore file
├── code/                        # Analysis scripts
│   ├── preprocessing.py         # Data cleaning and preparation (Step 1)
│   ├── spatial.py               # Spatial analysis and mapping (Step 2)
│   ├── plot_spatial.py          # Spatial visualization (Step 3)
│   ├── eda.py                   # Exploratory data analysis (Step 4)
│   ├── regression_analysis.py   # Statistical modeling (Step 5)
│   └── app.py                   # Interactive Streamlit dashboard
└── data/                        # Data directory
    ├── raw-data/                # Original data sources
    └── derived-data/            # Processed and intermediate data
```

## Data Sources

The project utilizes multiple data sources:

- **Chicago Public Schools (CPS) School Data**: Academic performance metrics, graduation rates, and demographic information
- **American Community Survey (ACS)**: Neighborhood socioeconomic indicators
- **Chicago Neighborhood Boundaries**: Geographic data for spatial analysis
- **Census Data**: Additional demographic and economic indicators

## Key Variables

### Neighborhood Disadvantage Index (NDI)

A composite measure calculated from:

- Poverty rate
- Unemployment rate
- Educational attainment
- Median household income
- Other socioeconomic indicators

### Educational Outcomes

- **Graduation Rate**: Percentage of students graduating within 4 years
- **College Enrollment Rate**: Percentage of graduates enrolling in college
- **Transition Gap**: Difference in outcomes between demographic groups

## Methodology

1. **Data Integration**: Merge school-level data with neighborhood socioeconomic indicators
2. **Index Construction**: Create Neighborhood Disadvantage Index using principal component analysis
3. **Spatial Analysis**: Map educational outcomes and disadvantage scores across Chicago
4. **Statistical Modeling**: Regression analysis to quantify relationships
5. **Visualization**: Create interactive maps and dashboards

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/final-project-yijia-ruilin-ruoyan.git
cd final-project-yijia-ruilin-ruoyan
```

### 2. Create Conda Environment

```bash
conda env create -f environment.yml
conda activate cps-analysis
```

### 3. Prepare Data

Place raw data files in the `data/raw-data/` directory. The expected files include:

- CPS school performance data
- ACS socioeconomic data
- Chicago neighborhood shapefiles

### 4. Run Analysis Pipeline

Execute scripts in the following order:

```bash
# 1. Preprocess data
python code/preprocessing.py

# 2. Spatial analysis
python code/spatial.py

# 3. Generate spatial plots
python code/plot_spatial.py

# 4. Exploratory data analysis
python code/eda.py

# 5. Regression analysis
python code/regression_analysis.py
```

### 5. Launch Interactive Dashboard

```bash
streamlit run code/app.py
```

## Analysis Pipeline

### Step 1: Data Preprocessing (`preprocessing.py`)

- Clean and merge multiple data sources
- Handle missing values and outliers
- Create consistent geographic identifiers
- Generate initial derived variables

### Step 2: Spatial Analysis (`spatial.py`)

- Geospatial data integration
- Neighborhood disadvantage index calculation
- Spatial autocorrelation analysis
- Hotspot and coldspot identification

### Step 3: Spatial Visualization (`plot_spatial.py`)

- Choropleth maps of disadvantage and outcomes
- Spatial pattern visualization
- Comparative analysis across neighborhoods
- Geographic distribution plots

### Step 4: Exploratory Data Analysis (`eda.py`)

- Summary statistics and distributions
- Correlation analysis
- Data quality checks
- Initial visualization of relationships
- Descriptive analysis of key variables

### Step 5: Statistical Modeling (`regression_analysis.py`)

- Linear regression models
- Model diagnostics and validation
- Interpretation of coefficients
- Visualization of regression results
- Hypothesis testing and inference

## Interactive Dashboard

The project includes an interactive Streamlit dashboard (`app.py`) that allows users to:

- Explore spatial patterns of educational outcomes
- Filter schools by various characteristics
- Visualize relationships between disadvantage and outcomes
- Compare different neighborhoods
- Download customized visualizations

## Key Findings

*(To be populated with actual results after analysis)*

1. **Strong Correlation**: Neighborhood disadvantage shows a significant negative correlation with graduation rates
2. **Spatial Patterns**: Clear geographic clustering of both disadvantage and educational outcomes
3. **Demographic Differences**: The impact of neighborhood context varies across student subgroups
4. **Policy Implications**: Targeted interventions in high-disadvantage neighborhoods could improve educational equity

## Technical Details

### Dependencies

- Python 3.11
- pandas, numpy, scipy
- geopandas, shapely
- matplotlib, seaborn, plotly
- statsmodels, scikit-learn
- streamlit, folium
- jupyter, notebook

### Computational Requirements

- Minimum: 8GB RAM, 10GB disk space
- Recommended: 16GB RAM for spatial analysis
- All analysis can be run on standard laptops

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with appropriate documentation
4. Submit a pull request

## Authors

- Yijia
- Ruilin Yao
- Ruoyan

## Course Information

**PPHA-30538: Advanced Data Analytics for Public Policy**
University of Chicago, Winter 2026

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Chicago Public Schools for data access
- American Community Survey for socioeconomic data
- University of Chicago Harris School of Public Policy
- Course instructors and teaching assistants

## References

1. Chicago Public Schools. (2024). School Progress Reports.
2. U.S. Census Bureau. (2024). American Community Survey.
3. Sampson, R. J., et al. (1997). Neighborhoods and violent crime.
4. Reardon, S. F. (2011). The widening academic achievement gap.

## Contact

For questions about this project, please contact the authors or create an issue in the GitHub repository.
