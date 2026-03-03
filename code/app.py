#!/usr/bin/env python3
"""
Interactive Dashboard for CPS School Analysis
Streamlit app for visualizing neighborhood disadvantage and school outcomes
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path
import folium
from streamlit_folium import folium_static
import seaborn as sns

# ---------- Configuration ----------
st.set_page_config(
    page_title="CPS School Analysis Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Paths ----------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DERIVED_DATA_DIR = PROJECT_ROOT / "data" / "derived-data"

# ---------- Load Data ----------
@st.cache_data
def load_data():
    """Load all necessary data files"""
    try:
        # Load school data with neighborhood disadvantage index
        schools_path = DERIVED_DATA_DIR / "schools_with_ndi.csv"
        schools = pd.read_csv(schools_path)
        
        # Load ACS data with PCA scores
        acs_path = DERIVED_DATA_DIR / "acs_with_pca_score.csv"
        acs = pd.read_csv(acs_path)
        
        # Load regression results
        reg_results_path = DERIVED_DATA_DIR / "regression_results_summary.csv"
        reg_results = pd.read_csv(reg_results_path)
        
        # Load descriptive statistics
        desc_stats_path = DERIVED_DATA_DIR / "regression_descriptive_stats.csv"
        desc_stats = pd.read_csv(desc_stats_path, index_col=0)
        
        # Load spatial data if available
        schools_gdf = None
        tracts_gdf = None
        try:
            schools_gpkg_path = DERIVED_DATA_DIR / "schools_with_ndi.gpkg"
            if schools_gpkg_path.exists():
                schools_gdf = gpd.read_file(schools_gpkg_path)
            
            tracts_gpkg_path = DERIVED_DATA_DIR / "tracts_with_ndi.gpkg"
            if tracts_gpkg_path.exists():
                tracts_gdf = gpd.read_file(tracts_gpkg_path)
        except Exception as e:
            st.warning(f"Could not load spatial data: {e}")
        
        return schools, acs, reg_results, desc_stats, schools_gdf, tracts_gdf
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None, None, None

# ---------- Main App ----------
def main():
    st.title("CPS School Analysis Dashboard")
    st.markdown("""
    **Exploring the relationship between neighborhood disadvantage and school outcomes**  
    *Does graduating from a CPS high school translate equally into college enrollment across neighborhoods?*
    """)
    
    # Load data
    with st.spinner("Loading data..."):
        schools, acs, reg_results, desc_stats, schools_gdf, tracts_gdf = load_data()
    
    if schools is None:
        st.error("Failed to load data. Please check data files.")
        return
    
    # ---------- Sidebar ----------
    st.sidebar.title("Dashboard Controls")
    
    # Data overview
    st.sidebar.markdown("### Data Overview")
    st.sidebar.info(f"""
    - **Schools**: {len(schools):,}
    - **Census Tracts**: {len(acs):,}
    - **Variables**: 1 neighborhood disadvantage index + 3 school outcomes
    """)
    
    # Navigation
    st.sidebar.markdown("### Navigation")
    page = st.sidebar.radio(
        "Select Section",
        ["Overview", "School Analysis", "Spatial Analysis", "Regression Results", "Detailed Analysis"]
    )
    
    # Filter controls
    st.sidebar.markdown("### Filters")
    
    # School type filter
    if 'Primary_Category' in schools.columns:
        school_types = schools['Primary_Category'].unique()
        selected_types = st.sidebar.multiselect(
            "School Types",
            options=school_types,
            default=school_types.tolist()
        )
        schools_filtered = schools[schools['Primary_Category'].isin(selected_types)]
    else:
        schools_filtered = schools.copy()
    
    # Disadvantage score filter
    if 'disadvantage_score' in schools_filtered.columns:
        min_score = float(schools_filtered['disadvantage_score'].min())
        max_score = float(schools_filtered['disadvantage_score'].max())
        score_range = st.sidebar.slider(
            "Neighborhood Disadvantage Score Range",
            min_value=min_score,
            max_value=max_score,
            value=(min_score, max_score),
            step=0.1
        )
        schools_filtered = schools_filtered[
            (schools_filtered['disadvantage_score'] >= score_range[0]) &
            (schools_filtered['disadvantage_score'] <= score_range[1])
        ]
    
    # ---------- Page 1: Overview ----------
    if page == "Overview":
        st.header("Project Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### Research Question
            **Does graduating from a CPS high school translate equally into college enrollment 
            across neighborhoods, or does neighborhood disadvantage weaken the transition from 
            high school completion to postsecondary opportunity?**
            
            ### Key Variables
            - **Neighborhood Disadvantage Index**: PCA-based score from ACS data
            - **Graduation Rate**: 4-year graduation percentage
            - **College Enrollment Rate**: Post-secondary enrollment percentage  
            - **Transition Gap**: Graduation Rate - College Enrollment Rate
            """)
        
        with col2:
            st.markdown("""
            ### Data Sources
            1. **Chicago Public Schools (CPS)** - School-level outcomes
            2. **American Community Survey (ACS)** - Neighborhood characteristics
            3. **Chicago Census Tract boundary shapefile** - Geographic boundaries for spatial linkage
            
            ### Methodology
            1. Construct Neighborhood Disadvantage Index using PCA
            2. Spatial join schools to census tracts
            3. Analyze relationships using regression models
            4. Visualize spatial patterns
            """)
        
        # Key statistics
        st.subheader("Key Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_grad = schools_filtered['Graduation_4_Year_School_Pct_Year_2'].mean()
            st.metric("Average Graduation Rate", f"{avg_grad:.1f}%")
        
        with col2:
            avg_enroll = schools_filtered['College_Enrollment_School_Pct_Year_2'].mean()
            st.metric("Average College Enrollment", f"{avg_enroll:.1f}%")
        
        with col3:
            avg_gap = schools_filtered['Transition_Gap'].mean()
            st.metric("Average Transition Gap", f"{avg_gap:.1f}%")
        
        with col4:
            avg_ndi = schools_filtered['disadvantage_score'].mean()
            st.metric("Average Disadvantage Score", f"{avg_ndi:.2f}")
        
        # Distribution plots
        st.subheader("Outcome Distributions")
        
        fig = go.Figure()
        
        # Add histograms for each outcome
        fig.add_trace(go.Histogram(
            x=schools_filtered['Graduation_4_Year_School_Pct_Year_2'],
            name='Graduation Rate',
            opacity=0.7,
            nbinsx=30
        ))
        
        fig.add_trace(go.Histogram(
            x=schools_filtered['College_Enrollment_School_Pct_Year_2'],
            name='College Enrollment',
            opacity=0.7,
            nbinsx=30
        ))
        
        fig.add_trace(go.Histogram(
            x=schools_filtered['Transition_Gap'],
            name='Transition Gap',
            opacity=0.7,
            nbinsx=30
        ))
        
        fig.update_layout(
            title='Distribution of School Outcomes',
            xaxis_title='Percentage (%)',
            yaxis_title='Count',
            barmode='overlay',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Correlation matrix
        st.subheader("Correlation Matrix")
        
        corr_vars = ['Graduation_4_Year_School_Pct_Year_2', 
                    'College_Enrollment_School_Pct_Year_2',
                    'Transition_Gap', 
                    'disadvantage_score']
        
        if all(var in schools_filtered.columns for var in corr_vars):
            corr_matrix = schools_filtered[corr_vars].corr()
            
            fig = px.imshow(
                corr_matrix,
                text_auto='.2f',
                color_continuous_scale='RdBu',
                range_color=[-1, 1],
                title='Correlation Between Variables'
            )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
    
    # ---------- Page 2: School Analysis ----------
    elif page == "School Analysis":
        st.header("School-Level Analysis")
        
        # Scatter plots
        st.subheader("Relationship Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Graduation vs Disadvantage
            fig = px.scatter(
                schools_filtered,
                x='disadvantage_score',
                y='Graduation_4_Year_School_Pct_Year_2',
                hover_data=['Long_Name', 'Primary_Category'],
                trendline='ols',
                title='Graduation Rate vs Neighborhood Disadvantage',
                labels={
                    'disadvantage_score': 'Neighborhood Disadvantage Score',
                    'Graduation_4_Year_School_Pct_Year_2': 'Graduation Rate (%)'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Enrollment vs Disadvantage
            fig = px.scatter(
                schools_filtered,
                x='disadvantage_score',
                y='College_Enrollment_School_Pct_Year_2',
                hover_data=['Long_Name', 'Primary_Category'],
                trendline='ols',
                title='College Enrollment vs Neighborhood Disadvantage',
                labels={
                    'disadvantage_score': 'Neighborhood Disadvantage Score',
                    'College_Enrollment_School_Pct_Year_2': 'College Enrollment Rate (%)'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Transition Gap analysis
        st.subheader("Transition Gap Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Transition Gap vs Disadvantage
            fig = px.scatter(
                schools_filtered,
                x='disadvantage_score',
                y='Transition_Gap',
                hover_data=['Long_Name', 'Primary_Category'],
                trendline='ols',
                title='Transition Gap vs Neighborhood Disadvantage',
                labels={
                    'disadvantage_score': 'Neighborhood Disadvantage Score',
                    'Transition_Gap': 'Transition Gap (%)'
                },
                color='Transition_Gap',
                color_continuous_scale='RdYlBu_r'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top schools with largest gaps
            st.markdown("### Schools with Largest Transition Gaps")
            
            top_gaps = schools_filtered.nlargest(10, 'Transition_Gap')[['Long_Name', 'Transition_Gap', 'Graduation_4_Year_School_Pct_Year_2', 'College_Enrollment_School_Pct_Year_2']]
            top_gaps = top_gaps.rename(columns={
                'Long_Name': 'School Name',
                'Transition_Gap': 'Gap (%)',
                'Graduation_4_Year_School_Pct_Year_2': 'Grad Rate (%)',
                'College_Enrollment_School_Pct_Year_2': 'Enroll Rate (%)'
            })
            
            st.dataframe(
                top_gaps.style.format({
                    'Gap (%)': '{:.1f}%',
                    'Grad Rate (%)': '{:.1f}%',
                    'Enroll Rate (%)': '{:.1f}%'
                }).background_gradient(subset=['Gap (%)'], cmap='Reds'),
                use_container_width=True
            )
        
        # Interactive table
        st.subheader("School Data Table")
        
        display_cols = ['Long_Name', 'Primary_Category', 
                       'Graduation_4_Year_School_Pct_Year_2',
                       'College_Enrollment_School_Pct_Year_2',
                       'Transition_Gap', 'disadvantage_score']
        
        if all(col in schools_filtered.columns for col in display_cols):
            display_df = schools_filtered[display_cols].copy()
            display_df = display_df.rename(columns={
                'Long_Name': 'School Name',
                'Primary_Category': 'School Type',
                'Graduation_4_Year_School_Pct_Year_2': 'Grad Rate (%)',
                'College_Enrollment_School_Pct_Year_2': 'Enroll Rate (%)',
                'Transition_Gap': 'Gap (%)',
                'disadvantage_score': 'Disadvantage Score'
            })
            
            # Format percentages
            for col in ['Grad Rate (%)', 'Enroll Rate (%)', 'Gap (%)']:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.1f}%" if pd.notnull(x) else "")
            
            st.dataframe(
                display_df.sort_values('Gap (%)', ascending=False),
                use_container_width=True,
                height=400
            )
    
    # ---------- Page 3: Spatial Analysis ----------
    elif page == "Spatial Analysis":
        st.header("Spatial Analysis")
        
        if schools_gdf is None or tracts_gdf is None:
            st.warning("Spatial data not available. Showing tabular data instead.")
            
            # Show neighborhood disadvantage distribution
            st.subheader("Neighborhood Disadvantage Distribution")
            
            fig = px.histogram(
                acs,
                x='disadvantage_score',
                nbins=50,
                title='Distribution of Neighborhood Disadvantage Scores',
                labels={'disadvantage_score': 'Disadvantage Score', 'count': 'Number of Census Tracts'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show top disadvantaged neighborhoods
            st.subheader("Most Disadvantaged Neighborhoods")
            
            top_disadvantaged = acs.nlargest(10, 'disadvantage_score')[['NAME', 'disadvantage_score', 'poverty_rate']]
            top_disadvantaged = top_disadvantaged.rename(columns={
                'NAME': 'Census Tract',
                'disadvantage_score': 'Disadvantage Score',
                'poverty_rate': 'Poverty Rate'
            })
            
            st.dataframe(
                top_disadvantaged.style.format({
                    'Disadvantage Score': '{:.2f}',
                    'Poverty Rate': '{:.1%}'
                }).background_gradient(subset=['Disadvantage Score'], cmap='Reds'),
                use_container_width=True
            )
        else:
            # Create interactive map
            st.subheader("Interactive Map")
            
            # Map type selector
            map_type = st.selectbox(
                "Select Map Layer",
                ["Neighborhood Disadvantage", "School Graduation Rates", 
                 "School College Enrollment", "School Transition Gaps"]
            )
            
            # Create Folium map
            m = folium.Map(location=[41.8781, -87.6298], zoom_start=10)
            
            # Add tract boundaries as background for all map types
            folium.GeoJson(
                tracts_gdf,
                name='Tract Boundaries',
                style_function=lambda x: {
                    'fillColor': 'transparent',
                    'color': 'gray',
                    'weight': 0.5,
                    'fillOpacity': 0
                }
            ).add_to(m)
            
            if map_type == "Neighborhood Disadvantage":
                # Choropleth for neighborhood disadvantage
                folium.Choropleth(
                    geo_data=tracts_gdf.__geo_interface__,
                    data=acs,
                    columns=['GEOID', 'disadvantage_score'],
                    key_on='feature.properties.GEOID',
                    fill_color='RdYlBu_r',
                    fill_opacity=0.7,
                    line_opacity=0.2,
                    legend_name='Neighborhood Disadvantage Score',
                    bins=7
                ).add_to(m)
                
                # Add school points
                for idx, row in schools_gdf.iterrows():
                    if pd.notnull(row['School_Latitude']) and pd.notnull(row['School_Longitude']):
                        popup_text = f"""
                        <b>{row['Long_Name']}</b><br>
                        Graduation: {row['Graduation_4_Year_School_Pct_Year_2']:.1f}%<br>
                        College Enrollment: {row['College_Enrollment_School_Pct_Year_2']:.1f}%<br>
                        Transition Gap: {row['Transition_Gap']:.1f}%
                        """
                        folium.CircleMarker(
                            location=[row['School_Latitude'], row['School_Longitude']],
                            radius=5,
                            color='black',
                            fill=True,
                            fill_color='white',
                            fill_opacity=0.7,
                            popup=folium.Popup(popup_text, max_width=300)
                        ).add_to(m)
            
            elif map_type == "School Graduation Rates":
                # Color schools by graduation rate
                for idx, row in schools_gdf.iterrows():
                    if pd.notnull(row['School_Latitude']) and pd.notnull(row['School_Longitude']):
                        # Color based on graduation rate
                        grad_rate = row['Graduation_4_Year_School_Pct_Year_2']
                        if pd.notnull(grad_rate):
                            if grad_rate >= 90:
                                color = 'green'
                            elif grad_rate >= 80:
                                color = 'lightgreen'
                            elif grad_rate >= 70:
                                color = 'yellow'
                            elif grad_rate >= 60:
                                color = 'orange'
                            else:
                                color = 'red'
                            
                            popup_text = f"""
                            <b>{row['Long_Name']}</b><br>
                            Graduation: {grad_rate:.1f}%<br>
                            College Enrollment: {row['College_Enrollment_School_Pct_Year_2']:.1f}%<br>
                            Transition Gap: {row['Transition_Gap']:.1f}%
                            """
                            folium.CircleMarker(
                                location=[row['School_Latitude'], row['School_Longitude']],
                                radius=8,
                                color=color,
                                fill=True,
                                fill_color=color,
                                fill_opacity=0.7,
                                popup=folium.Popup(popup_text, max_width=300)
                            ).add_to(m)
            
            elif map_type == "School College Enrollment":
                # Color schools by college enrollment rate
                for idx, row in schools_gdf.iterrows():
                    if pd.notnull(row['School_Latitude']) and pd.notnull(row['School_Longitude']):
                        # Color based on college enrollment rate
                        enroll_rate = row['College_Enrollment_School_Pct_Year_2']
                        if pd.notnull(enroll_rate):
                            if enroll_rate >= 80:
                                color = 'green'
                            elif enroll_rate >= 60:
                                color = 'lightgreen'
                            elif enroll_rate >= 40:
                                color = 'yellow'
                            elif enroll_rate >= 20:
                                color = 'orange'
                            else:
                                color = 'red'
                            
                            popup_text = f"""
                            <b>{row['Long_Name']}</b><br>
                            Graduation: {row['Graduation_4_Year_School_Pct_Year_2']:.1f}%<br>
                            College Enrollment: {enroll_rate:.1f}%<br>
                            Transition Gap: {row['Transition_Gap']:.1f}%
                            """
                            folium.CircleMarker(
                                location=[row['School_Latitude'], row['School_Longitude']],
                                radius=8,
                                color=color,
                                fill=True,
                                fill_color=color,
                                fill_opacity=0.7,
                                popup=folium.Popup(popup_text, max_width=300)
                            ).add_to(m)
            
            elif map_type == "School Transition Gaps":
                # Color schools by transition gap
                for idx, row in schools_gdf.iterrows():
                    if pd.notnull(row['School_Latitude']) and pd.notnull(row['School_Longitude']):
                        # Color based on transition gap
                        gap = row['Transition_Gap']
                        if pd.notnull(gap):
                            # For gap, lower is better (smaller gap)
                            if gap <= 10:
                                color = 'green'
                            elif gap <= 20:
                                color = 'lightgreen'
                            elif gap <= 30:
                                color = 'yellow'
                            elif gap <= 40:
                                color = 'orange'
                            else:
                                color = 'red'
                            
                            popup_text = f"""
                            <b>{row['Long_Name']}</b><br>
                            Graduation: {row['Graduation_4_Year_School_Pct_Year_2']:.1f}%<br>
                            College Enrollment: {row['College_Enrollment_School_Pct_Year_2']:.1f}%<br>
                            Transition Gap: {gap:.1f}%
                            """
                            folium.CircleMarker(
                                location=[row['School_Latitude'], row['School_Longitude']],
                                radius=8,
                                color=color,
                                fill=True,
                                fill_color=color,
                                fill_opacity=0.7,
                                popup=folium.Popup(popup_text, max_width=300)
                            ).add_to(m)
            
            # Display map
            folium_static(m, width=1000, height=600)
            
            # Map statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Schools Mapped", len(schools_gdf))
            
            with col2:
                avg_lat = schools_gdf['School_Latitude'].mean()
                avg_lon = schools_gdf['School_Longitude'].mean()
                st.metric("Average Location", f"{avg_lat:.4f}, {avg_lon:.4f}")
            
            with col3:
                if 'Transition_Gap' in schools_gdf.columns:
                    max_gap = schools_gdf['Transition_Gap'].max()
                    st.metric("Maximum Transition Gap", f"{max_gap:.1f}%")
    
    # ---------- Page 4: Regression Results ----------
    elif page == "Regression Results":
        st.header("Regression Analysis Results")
        
        if reg_results is not None:
            # Display regression results table
            st.subheader("Regression Summary")
            
            # Format the table
            display_reg = reg_results.copy()
            display_reg = display_reg.rename(columns={
                'Model': 'Model',
                'Dependent Variable': 'Outcome',
                'Coefficient': 'Coefficient',
                'Std Error': 'Std Error',
                'P-value': 'P-value',
                'R-squared': 'R²',
                'N': 'N'
            })
            
            # Format numbers
            display_reg['Coefficient'] = display_reg['Coefficient'].apply(lambda x: f"{x:.3f}")
            display_reg['Std Error'] = display_reg['Std Error'].apply(lambda x: f"{x:.3f}")
            display_reg['P-value'] = display_reg['P-value'].apply(lambda x: f"{x:.4f}")
            display_reg['R²'] = display_reg['R²'].apply(lambda x: f"{x:.3f}")
            
            st.dataframe(display_reg, use_container_width=True)
            
            # Interpretation
            st.subheader("Interpretation")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### Graduation Model")
                coef = reg_results.iloc[0]['Coefficient']
                pval = reg_results.iloc[0]['P-value']
                
                if pval < 0.05:
                    if coef < 0:
                        st.success("✅ **Statistically significant**")
                        st.markdown(f"""
                        - Coefficient: **{coef:.3f}**
                        - For each 1-unit increase in disadvantage score,
                          graduation rate decreases by **{abs(coef):.2f} percentage points**
                        """)
                    else:
                        st.warning("⚠️ **Unexpected positive relationship**")
                else:
                    st.info("ℹ️ **Not statistically significant**")
            
            with col2:
                st.markdown("### Enrollment Model")
                coef = reg_results.iloc[1]['Coefficient']
                pval = reg_results.iloc[1]['P-value']
                
                if pval < 0.05:
                    if coef < 0:
                        st.success("✅ **Statistically significant**")
                        st.markdown(f"""
                        - Coefficient: **{coef:.3f}**
                        - For each 1-unit increase in disadvantage score,
                          college enrollment decreases by **{abs(coef):.2f} percentage points**
                        - Stronger effect than on graduation
                        """)
                    else:
                        st.warning("⚠️ **Unexpected positive relationship**")
                else:
                    st.info("ℹ️ **Not statistically significant**")
            
            with col3:
                st.markdown("### Transition Gap Model")
                coef = reg_results.iloc[2]['Coefficient']
                pval = reg_results.iloc[2]['P-value']
                
                if pval < 0.1:  # Using 0.1 threshold for borderline significance
                    if coef > 0:
                        st.success("✅ **Marginally significant**")
                        st.markdown(f"""
                        - Coefficient: **{coef:.3f}**
                        - For each 1-unit increase in disadvantage score,
                          transition gap increases by **{coef:.2f} percentage points**
                        - Supports hypothesis: disadvantage weakens transition
                        """)
                    else:
                        st.warning("⚠️ **Unexpected negative relationship**")
                else:
                    st.info("ℹ️ **Not statistically significant**")
            
            # Visualize coefficients
            st.subheader("Coefficient Visualization")
            
            fig = go.Figure()
            
            # Add coefficient bars with error bars
            for i, row in reg_results.iterrows():
                fig.add_trace(go.Bar(
                    x=[row['Model']],
                    y=[row['Coefficient']],
                    error_y=dict(
                        type='data',
                        array=[row['Std Error'] * 1.96],
                        visible=True
                    ),
                    name=row['Model'].split('~')[0].strip(),
                    text=f"{row['Coefficient']:.3f}",
                    textposition='auto',
                    marker_color='red' if row['Coefficient'] < 0 else 'green'
                ))
            
            fig.update_layout(
                title='Regression Coefficients with 95% Confidence Intervals',
                xaxis_title='Model',
                yaxis_title='Coefficient',
                showlegend=False,
                height=400
            )
            
            # Add zero line
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show scatter plots from saved images
            st.subheader("Regression Scatter Plots")
            
            try:
                # Try to load and display the saved regression plots
                import base64
                from PIL import Image
                import io
                
                plot_path = DERIVED_DATA_DIR / "regression_scatter_plots.png"
                if plot_path.exists():
                    image = Image.open(plot_path)
                    st.image(image, caption="Regression Scatter Plots", use_container_width=True)
                
                coef_plot_path = DERIVED_DATA_DIR / "regression_coefficients_plot.png"
                if coef_plot_path.exists():
                    image = Image.open(coef_plot_path)
                    st.image(image, caption="Regression Coefficients Plot", use_container_width=True)
            except Exception as e:
                st.warning(f"Could not load saved plots: {e}")
    
    # ---------- Page 5: Detailed Analysis ----------
    elif page == "Detailed Analysis":
        st.header("Detailed Analysis")
        
        # Neighborhood indicators analysis
        st.subheader("Neighborhood Indicators")
        
        if acs is not None:
            # Select indicators to visualize
            indicators = ['poverty_rate', 'unemployment_rate', 'single_parent_rate', 'rent_burden_rate']
            indicator_names = {
                'poverty_rate': 'Poverty Rate',
                'unemployment_rate': 'Unemployment Rate',
                'single_parent_rate': 'Single Parent Households',
                'rent_burden_rate': 'Rent Burden'
            }
            
            selected_indicator = st.selectbox(
                "Select Neighborhood Indicator",
                options=indicators,
                format_func=lambda x: indicator_names[x]
            )
            
            # Create distribution plot
            fig = px.histogram(
                acs,
                x=selected_indicator,
                nbins=30,
                title=f'Distribution of {indicator_names[selected_indicator]}',
                labels={selected_indicator: indicator_names[selected_indicator], 'count': 'Number of Census Tracts'}
            )
            
            # Add mean line
            mean_val = acs[selected_indicator].mean()
            fig.add_vline(x=mean_val, line_dash="dash", line_color="red", 
                         annotation_text=f"Mean: {mean_val:.3f}")
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Correlation with disadvantage score
            st.subheader("Correlation with Disadvantage Score")
            
            corr_with_ndi = acs[indicators + ['disadvantage_score']].corr()['disadvantage_score'].drop('disadvantage_score')
            
            fig = px.bar(
                x=corr_with_ndi.index,
                y=corr_with_ndi.values,
                labels={'x': 'Indicator', 'y': 'Correlation with Disadvantage Score'},
                title='Correlation of Indicators with Disadvantage Score',
                color=corr_with_ndi.values,
                color_continuous_scale='RdBu',
                range_color=[-1, 1]
            )
            
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Advanced analysis options
        st.subheader("Advanced Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### Potential Extensions
            
            1. **Interaction Effects**
               - Test if the relationship varies by school type
               - Graduation × Disadvantage interaction
            
            2. **Non-linear Relationships**
               - Quadratic terms for disadvantage
               - Threshold effects
            
            3. **Spatial Autocorrelation**
               - Moran's I test
               - Spatial regression models
            """)
        
        with col2:
            st.markdown("""
            ### Policy Implications
            
            1. **Targeted Interventions**
               - Focus on schools with large transition gaps
               - Neighborhood-based support programs
            
            2. **College Access Programs**
               - Bridge programs for high-disadvantage schools
               - Mentorship and counseling
            
            3. **Resource Allocation**
               - Direct resources to weakest transitions
               - Performance-based funding
            """)
        
        # Download data
        st.subheader("Download Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Convert schools data to CSV for download
            csv = schools_filtered.to_csv(index=False)
            st.download_button(
                label="Download School Data (CSV)",
                data=csv,
                file_name="cps_schools_analysis.csv",
                mime="text/csv"
            )
        
        with col2:
            # Convert regression results to CSV
            if reg_results is not None:
                reg_csv = reg_results.to_csv(index=False)
                st.download_button(
                    label="Download Regression Results (CSV)",
                    data=reg_csv,
                    file_name="regression_results.csv",
                    mime="text/csv"
                )
        
        with col3:
            # Convert ACS data to CSV
            if acs is not None:
                acs_csv = acs.to_csv(index=False)
                st.download_button(
                    label="Download ACS Data (CSV)",
                    data=acs_csv,
                    file_name="acs_neighborhood_data.csv",
                    mime="text/csv"
                )
    
    # ---------- Footer ----------
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Data Sources**
        - Chicago Public Schools
        - American Community Survey
        - Chicago Census Tract boundaries
        """)
    
    with col2:
        st.markdown("""
        **Methodology**
        - PCA for index construction
        - Spatial analysis
        - Regression modeling
        """)
    
    with col3:
        st.markdown("""
        **Contact**
        - PPHA 30538 Final Project
        - Winter 2026
        - University of Chicago
        """)

if __name__ == "__main__":
    main()