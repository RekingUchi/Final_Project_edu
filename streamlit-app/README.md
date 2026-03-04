# CPS School Analysis Dashboard

An interactive Streamlit dashboard for analyzing the relationship between neighborhood disadvantage and educational outcomes in Chicago Public Schools.

## Deployment on Streamlit Community Cloud

This app is deployed at: **https://finalprojectedu-yzsqwibcccux3vecgrtaqb.streamlit.app/**

### How to Deploy

1. **Upload your data files** to the Streamlit Cloud:
   - Navigate to your Streamlit Cloud dashboard
   - Upload the following files to the `data` directory:
     - `schools_with_ndi.csv`
     - `acs_with_pca_score.csv`
     - `regression_results_summary.csv` (optional)
     - `regression_descriptive_stats.csv` (optional)
     - `schools_with_ndi.gpkg` (optional, for spatial analysis)
     - `tracts_with_ndi.gpkg` (optional, for spatial analysis)

2. **Connect your GitHub repository** containing this code

3. **Configure deployment settings**:
   - Main file path: `app.py`
   - Python version: 3.8+

## App Features

### Dashboard Sections

1. **Overview**: Project introduction and key statistics
2. **School Analysis**: Interactive scatter plots and school-level data
3. **Spatial Analysis**: Interactive maps showing geographic patterns
4. **Regression Results**: Statistical analysis and interpretation
5. **Detailed Analysis**: Advanced insights and policy implications

### Key Features

- Interactive filtering by school type and disadvantage score
- Real-time data visualization with Plotly
- Interactive maps with Folium
- Statistical analysis results
- Data download capabilities
- Responsive design for different screen sizes

## Data Requirements

The app requires the following processed data files:

### Required Files
- `schools_with_ndi.csv`: School data with neighborhood disadvantage scores
- `acs_with_pca_score.csv`: Census tract data with PCA-based disadvantage index

### Optional Files
- `regression_results_summary.csv`: Regression analysis results
- `regression_descriptive_stats.csv`: Descriptive statistics
- `schools_with_ndi.gpkg`: Geospatial school data
- `tracts_with_ndi.gpkg`: Geospatial tract boundaries

## Local Development

To run locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Project Information

- **Course**: PPHA 30538 - Winter 2026
- **Institution**: University of Chicago
- **Research Question**: Does graduating from a CPS high school translate equally into college enrollment across neighborhoods?

## Contact

For questions about this dashboard or the underlying analysis, please contact the project team.