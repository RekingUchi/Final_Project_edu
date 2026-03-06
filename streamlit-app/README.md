# CPS School Analysis - Streamlit Application

This folder contains the Streamlit application for the CPS School Analysis project.

## Live Application

**Access the live dashboard here:** [https://finalprojectedu-nxk4horjs9f7bmnigz4x2a.streamlit.app/](https://finalprojectedu-nxk4horjs9f7bmnigz4x2a.streamlit.app/)

## Local Development

### Prerequisites
- Python 3.11+
- pip package manager

### Installation

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

## Application Structure

```
streamlit-app/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                # This file
└── data/                    # Data files
    ├── schools_with_ndi.csv              # School data with neighborhood scores
    ├── acs_with_pca_score.csv            # ACS data with PCA scores
    ├── regression_results_summary.csv    # Regression analysis results
    ├── regression_descriptive_stats.csv  # Descriptive statistics
    ├── regression_scatter_plots.png      # Visualization images
    ├── regression_coefficients_plot.png  # Visualization images
    ├── schools_with_ndi.gpkg             # Geospatial school data
    └── tracts_with_ndi.gpkg              # Geospatial tract data
```

## Features

The Streamlit application provides:

### 1. **Overview Dashboard**
- Project introduction and methodology
- Key statistics and metrics
- Distribution visualizations
- Correlation analysis

### 2. **School Analysis**
- Interactive scatter plots
- School performance comparisons
- Transition gap analysis
- Filtering by school type and disadvantage score

### 3. **Spatial Analysis**
- Interactive maps of Chicago
- Multiple map layers:
  - Neighborhood disadvantage scores
  - School graduation rates
  - College enrollment rates
  - Transition gaps
- School location markers with detailed information

### 4. **Regression Results**
- Statistical model summaries
- Coefficient visualizations
- Interpretation of findings
- Policy implications

### 5. **Detailed Analysis**
- Neighborhood indicator distributions
- Advanced analysis options
- Data download capabilities

## Deployment

### Streamlit Cloud Deployment
The application is deployed on Streamlit Cloud. To deploy your own version:

1. Push this folder to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set the main file path to `app.py`
5. Deploy!

### Deployment Configuration
- **Main file**: `app.py`
- **Python version**: 3.11
- **Dependencies**: `requirements.txt`
- **Data files**: Included in the `data/` folder

## Data Sources

The application uses processed data from:
1. **Chicago Public Schools (CPS)** - School-level outcomes
2. **American Community Survey (ACS)** - Neighborhood characteristics
3. **Chicago Census Tract boundaries** - Geographic data

All data has been pre-processed and cleaned for the dashboard.

## Troubleshooting

### Common Issues

1. **Missing dependencies**: Ensure all packages in `requirements.txt` are installed
2. **Data file errors**: Check that all data files exist in the `data/` folder
3. **Geospatial issues**: Ensure geopandas and folium are properly installed
4. **Memory issues**: The application is optimized for web deployment

### Performance Tips
- The application uses caching for data loading
- Large geospatial files are loaded only when needed
- Images are pre-generated for faster loading

## Development

### Adding New Features
1. Modify `app.py` to add new sections
2. Add new data files to the `data/` folder if needed
3. Update `requirements.txt` for new dependencies
4. Test locally before deployment

### Code Structure
- **Data loading**: Cached functions in `load_data()`
- **Page navigation**: Sidebar radio buttons
- **Visualizations**: Plotly and Folium for interactive charts
- **Layout**: Streamlit columns and containers

## License

This application is part of the CPS School Analysis project for PPHA-30538, University of Chicago, Winter 2026.

## Contact

For questions about the application, please refer to the main project README or contact the project authors.

---

**Last Updated**: March 2026  
**Live URL**: [https://finalprojectedu-nxk4horjs9f7bmnigz4x2a.streamlit.app/](https://finalprojectedu-nxk4horjs9f7bmnigz4x2a.streamlit.app/)