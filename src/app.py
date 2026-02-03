import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
import json
import plotly.express as px
from streamlit_folium import st_folium

st.set_page_config(page_title="Glasgow Health Navigator", layout="wide")

# 1. Load Data & Metadata
@st.cache_data
def load_resources():
    gdf = gpd.read_parquet('data/processed/dashboard_data.parquet')
    with open('data/processed/indicator_metadata.json') as f:
        meta = json.load(f)
    return gdf, meta

gdf, metadata = load_resources()

# 2. Sidebar - Dynamic Dropdown
st.sidebar.header("📊 Filter Analytics")
all_options = metadata['indicators'] + ["park_count", "park_density"]
map_theme = st.sidebar.selectbox("Select Metric", options=all_options, 
                                 format_func=lambda x: x.replace("_", " ").title())

# Dynamic Slider
m_min, m_max = float(gdf[map_theme].min()), float(gdf[map_theme].max())
val_range = st.sidebar.slider(f"Range: {map_theme}", m_min, m_max, (m_min, m_max))

filtered_gdf = gdf[(gdf[map_theme] >= val_range[0]) & (gdf[map_theme] <= val_range[1])]

# 3. Layout: Map and Stats
col1, col2 = st.columns([3, 1])

with col1:
    m = folium.Map(location=[55.8642, -4.2518], zoom_start=12, tiles="CartoDB positron")
    folium.Choropleth(
        geo_data=filtered_gdf, data=filtered_gdf,
        columns=["DataZone", map_theme], key_on="feature.properties.DataZone",
        fill_color="YlGn" if "park" in map_theme else "RdYlGn",
        fill_opacity=0.7, line_opacity=0.2
    ).add_to(m)
    st_folium(m, width=900, height=500)

with col2:
    st.metric("Zones in View", len(filtered_gdf))
    st.metric("Avg Value", round(filtered_gdf[map_theme].mean(), 2))
    st.write("Top 5 Neighborhoods", filtered_gdf.nlargest(5, map_theme)[['Name', map_theme]])

# 4. Correlation Section
st.markdown("---")
st.header("📈 Correlation Analysis")
fig = px.scatter(filtered_gdf, x="SIMD2020_Health_Domain_Rank", y="park_density", 
                 hover_name="Name", trendline="ols", template="plotly_white")
st.plotly_chart(fig, use_container_width=True)
