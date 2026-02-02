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
                                  int(gdf.SIMD2020_Health_Domain_Rank.min()), 
                                  int(gdf.SIMD2020_Health_Domain_Rank.max()), 
                                  (1, 1000))

filtered_gdf = gdf[(gdf.SIMD2020_Health_Domain_Rank >= health_metric[0]) & 
                    (gdf.SIMD2020_Health_Domain_Rank <= health_metric[1])]

st.sidebar.markdown("---") # Visual separator
st.sidebar.subheader("Live Stats")

# Calculate metrics based on the filtered data
avg_health = filtered_gdf['SIMD2020_Health_Domain_Rank'].mean()
total_parks = filtered_gdf['park_count'].sum()
zone_count = len(filtered_gdf)

# Display as cards
st.sidebar.metric("Avg Health Rank", f"{int(avg_health)}")
st.sidebar.metric("Total Parks in View", f"{int(total_parks)}")
st.sidebar.metric("Zones Selected", f"{zone_count}")

map_theme = st.sidebar.selectbox(
    "Select Map Layer",
    options=["SIMD2020_Health_Domain_Rank", "park_count", "park_density"],
    format_func=lambda x: x.replace("_", " ").title() # Makes names look pretty
)


# 4. Visualization Layout
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader(f"Mapping: {map_theme.replace('_', ' ').title()}")
    
    # Create the map center at Glasgow coordinates
    m = folium.Map(location=[55.8642, -4.2518], zoom_start=12, tiles="CartoDB positron")

    # Add the choropleth layer
    folium.Choropleth(
        geo_data=filtered_gdf,
        name="Urban Data Overlay",
        data=filtered_gdf,
        columns=["DataZone", map_theme],  # <--- Changed from hardcoded string
        key_on="feature.properties.DataZone",
        # Logic to change colors: Green-Blue for parks, Red-Green for health
        fill_color="YlGn" if "park" in map_theme else "RdYlGn", 
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=map_theme.replace("_", " ").title()
    ).add_to(m)

    st_folium(m, width=900, height=600)

with col2:
    st.subheader("Stats Summary")
    st.metric("Visible Data Zones", len(filtered_gdf))
    st.metric("Avg Parks per Zone", round(filtered_gdf['park_count'].mean(), 2))
    
    # Show a raw data preview to prove engineering transparency
    st.write("Raw Attributes", filtered_gdf[['DataZone', 'SIMD2020_Health_Domain_Rank', 'park_count']].head())
