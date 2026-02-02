import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# 1. Config & Styling
st.set_page_config(page_title="Glasgow Urban Health Navigator", layout="wide")

st.title("🏙️ Glasgow Urban Resilience Dashboard")
st.markdown("""
This dashboard correlates **Health Deprivation (SIMD 2020)** with **Green Space Access** using your 10-year computational biology principles of spatial mapping.
""")

# 2. Data Loading (Fast because we pre-processed!)
@st.cache_data
def get_data():
    gdf = gpd.read_file('data/processed/dashboard_data.geojson')
    return gdf

gdf = get_data()

# 3. Sidebar Filters
st.sidebar.header("Filter Analytics")
# 'Health_domain_rank' is a common column name in SIMD
health_metric = st.sidebar.slider("Select Health Rank (Lower = More Deprived)", 
                                  int(gdf.Health_domain_rank.min()), 
                                  int(gdf.Health_domain_rank.max()), 
                                  (1, 1000))

filtered_gdf = gdf[(gdf.Health_domain_rank >= health_metric[0]) & 
                    (gdf.Health_domain_rank <= health_metric[1])]

# 4. Visualization Layout
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Spatial Distribution of Health vs. Greenery")
    
    # Create the map center at Glasgow coordinates
    m = folium.Map(location=[55.8642, -4.2518], zoom_start=12, tiles="CartoDB positron")

    # Add the choropleth layer
    folium.Choropleth(
        geo_data=filtered_gdf,
        name="Health Deprivation",
        data=filtered_gdf,
        columns=["DataZone", "Health_domain_rank"],
        key_on="feature.properties.DataZone",
        fill_color="RdYlGn", # Red-Yellow-Green (Standard health scale)
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Health Rank"
    ).add_to(m)

    st_folium(m, width=900, height=600)

with col2:
    st.subheader("Stats Summary")
    st.metric("Visible Data Zones", len(filtered_gdf))
    st.metric("Avg Parks per Zone", round(filtered_gdf['park_count'].mean(), 2))
    
    # Show a raw data preview to prove engineering transparency
    st.write("Raw Attributes", filtered_gdf[['DataZone', 'Health_domain_rank', 'park_count']].head())
