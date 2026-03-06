# CPS School Analysis: Neighborhood Disadvantage and Educational Outcomes

## Project Overview

This project analyzes the relationship between neighborhood socioeconomic disadvantage and educational outcomes in Chicago Public Schools (CPS). The study examines how neighborhood characteristics affect graduation rates, college enrollment rates, and transition gaps between different student demographic groups.

## 🚀 Live Interactive Dashboard

**Access the live application here:** [https://finalprojectedu-nxk4horjs9f7bmnigz4x2a.streamlit.app/](https://finalprojectedu-nxk4horjs9f7bmnigz4x2a.streamlit.app/)

The interactive dashboard allows you to:
- Explore spatial patterns of educational outcomes across Chicago
- Filter schools by various characteristics
- Visualize relationships between neighborhood disadvantage and school outcomes
- Compare different neighborhoods
- Download customized visualizations and data

## Research Questions

1. How does neighborhood socioeconomic disadvantage correlate with school-level graduation rates?
2. What is the relationship between neighborhood disadvantage and college enrollment rates?
3. How does neighborhood context affect the transition gap between different student groups?
4. Are there spatial patterns in educational outcomes across Chicago neighborhoods?

## Project Structure

```
Final_Project_edu/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore file
├── .devcontainer/               # Development container configuration
│   └── devcontainer.json
├── code/                        # Analysis scripts
│   ├── preprocessing.py         # Data cleaning and preparation (Step 1)
│   ├── spatial.py               # Spatial analysis and mapping (Step 2)
│   ├── plot_spatial.py          # Spatial visualization (Step 3)
│   ├── eda.py                   # Exploratory data analysis (Step 4)
│   ├── regression_analysis.py   # Statistical modeling (Step 5)
│   └── app.py                   # Interactive Streamlit dashboard
├── data/                        # Data directory
│   ├── raw-data/                # Original data sources
│   │   ├── CPS_data.csv
│   │   ├── acs_raw_chicago.csv
│   │   └── chicago_tracts_2010.kml
│   └── derived-data/            # Processed and intermediate data
│       ├── CPS_clean_data.csv
│       ├── acs_clean_chicago.csv
│       ├── acs_with_pca_score.csv
│       ├── schools_with_ndi.csv
│       ├── schools_with_ndi.gpkg
│       ├── tracts_with_ndi.gpkg
│       └── regression_results_summary.csv
├── streamlit-app/               # Streamlit deployment files
│   ├── app.py                   # Streamlit application
│   ├── requirements.txt         # Streamlit-specific dependencies
│   └── data/                    # Data for Streamlit app
│       ├── schools_with_ndi.csv
│       ├── acs_with_pca_score.csv
│       └── regression_results_summary.csv
├── final_project.qmd            # Quarto report source
├── final_project.html           # HTML report
├── final_project.pdf            # PDF report
└── final_project_files/         # Report assets
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
- **Transition Gap**: Difference between graduation rate and college enrollment rate

## Methodology

1. **Data Integration**: Merge school-level data with neighborhood socioeconomic indicators
2. **Index Construction**: Create Neighborhood Disadvantage Index using principal component analysis
3. **Spatial Analysis**: Map educational outcomes and disadvantage scores across Chicago
4. **Statistical Modeling**: Regression analysis to quantify relationships
5. **Visualization**: Create interactive maps and dashboards

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Final_Project_edu.git
cd Final_Project_edu
```

### 2. Create Virtual Environment

```bash
# Using conda
conda create -n cps-analysis python=3.11
conda activate cps-analysis

# Or using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare Data

Place raw data files in the `data/raw-data/` directory. The expected files include:
- CPS school performance data
- ACS socioeconomic data
- Chicago neighborhood shapefiles

### 5. Run Analysis Pipeline

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

### 6. Launch Interactive Dashboard Locally

```bash
streamlit run code/app.py
```

### 7. Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set the main file path to `code/app.py`
5. Deploy!

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

## Interactive Dashboard Features

The Streamlit dashboard (`code/app.py`) provides:

### 1. **Overview Section**
- Project introduction and methodology
- Key statistics and metrics
- Distribution visualizations
- Correlation matrix

### 2. **School Analysis**
- Scatter plots of outcomes vs. disadvantage
- Transition gap analysis
- Interactive data tables
- School performance rankings

### 3. **Spatial Analysis**
- Interactive maps of Chicago
- Multiple map layers:
  - Neighborhood disadvantage scores
  - School graduation rates
  - College enrollment rates
  - Transition gaps
- School location markers with detailed popups

### 4. **Regression Results**
- Statistical model summaries
- Coefficient visualizations with confidence intervals
- Interpretation of findings
- Policy implications

### 5. **Detailed Analysis**
- Neighborhood indicator distributions
- Advanced analysis options
- Data download capabilities

## Key Findings

*(Based on analysis results)*

1. **Strong Negative Correlation**: Neighborhood disadvantage shows a significant negative correlation with both graduation rates and college enrollment rates
2. **Stronger Effect on College Enrollment**: The negative relationship is stronger for college enrollment than for graduation rates
3. **Transition Gap Widening**: Schools in more disadvantaged neighborhoods tend to have larger transition gaps
4. **Spatial Clustering**: Clear geographic patterns with disadvantage concentrated in certain areas of Chicago
5. **Policy Implications**: Targeted interventions in high-disadvantage neighborhoods could significantly improve educational equity

## Technical Details

### Dependencies
- Python 3.11+
- pandas, numpy, scipy
- geopandas, shapely
- matplotlib, seaborn, plotly
- statsmodels, scikit-learn
- streamlit, folium, streamlit-folium

### Computational Requirements
- Minimum: 8GB RAM, 10GB disk space
- Recommended: 16GB RAM for spatial analysis
- All analysis can be run on standard laptops

### Deployment
The application is deployed on Streamlit Cloud:
- **URL**: https://finalprojectedu-nxk4horjs9f7bmnigz4x2a.streamlit.app/
- **Framework**: Streamlit 1.28+
- **Data**: All processed data included in deployment
- **Performance**: Optimized for web deployment with caching

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

---

**Last Updated**: March 2026  
**Live Dashboard**: [https://finalprojectedu-nxk4horjs9f7bmnigz4x2a.streamlit.app/](https://finalprojectedu-nxk4horjs9f7bmnigz4x2a.streamlit.app/)  
**GitHub Repository**: [https://github.com/yourusername/Final_Project_edu](https://github.com/yourusername/Final_Project_edu)