import streamlit as st
import geopandas as gpd
import folium
import json
from streamlit_folium import st_folium
from shapely.geometry import shape, Point
import plotly.express as px
import plotly.graph_objects as go

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

@st.cache_data
def get_park_points():
    with open('data/raw/glasgow_greenspace.json') as f:
        osm_data = json.load(f)
    
    # Extract centroids for each park feature to display as dots
    points = []
    for element in osm_data['elements']:
        if 'lat' in element and 'lon' in element:
            points.append({'geometry': Point(element['lon'], element['lat']), 'type': element.get('tags', {}).get('leisure', 'park')})
    
    return gpd.GeoDataFrame(points, crs="EPSG:4326")

gdf = get_data()
parks_points_gdf = get_park_points()


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

show_parks = st.sidebar.checkbox("Show Raw Park Locations", value=False)

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
        columns=["DataZone", map_theme], 
        key_on="feature.properties.DataZone",
        # Logic to change colors: Green-Blue for parks, Red-Green for health
        fill_color="YlGn" if "park" in map_theme else "RdYlGn", 
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=map_theme.replace("_", " ").title()
    ).add_to(m)

    # Park Dots
# REPLACE your 'if show_parks' loop with this:
    if show_parks:
        from folium.plugins import MarkerCluster
        marker_cluster = MarkerCluster(name="Park Locations").add_to(m)
        
        for _, row in parks_points_gdf.iterrows():
            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x],
                radius=3,
                color='darkgreen',
                fill=True,
                fill_color='green',
                fill_opacity=0.7,
                popup=row['type']
            ).add_to(marker_cluster)

    # Define the 'Invisible' interaction layer
    # This allows users to hover over polygons and see the data
    tooltip_layer = folium.features.GeoJson(
        filtered_gdf,
        style_function=lambda x: {'fillColor': '#ffffff', 'color':'#000000', 'fillOpacity': 0.0, 'weight': 0.1},
        highlight_function=lambda x: {'fillColor': '#000000', 'color':'#000000', 'fillOpacity': 0.2, 'weight': 1},
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Name', 'SIMD2020_Health_Domain_Rank', 'park_count', 'park_density'],
            aliases=['Neighborhood: ', 'Health Rank: ', 'Parks: ', 'Density (km2): '],
            localize=True,
            sticky=False,
            labels=True,
            style="""
                background-color: #F0EFEF;
                border: 2px solid black;
                border-radius: 3px;
                box-shadow: 3px;
            """,
            max_width=800,
        )
    )
    
    # Add this interaction layer to the map
    tooltip_layer.add_to(m)

    # Render the map in Streamlit
    st_folium(m, width=900, height=600)

with col2:
    st.subheader("Stats Summary")
    st.metric("Visible Data Zones", len(filtered_gdf))
    st.metric("Avg Parks per Zone", round(filtered_gdf['park_count'].mean(), 2))
    
    # Show a raw data preview to prove engineering transparency
    st.write("Raw Attributes", filtered_gdf[['DataZone', 'SIMD2020_Health_Domain_Rank', 'park_count']].head())

# 5. Correlation Analysis Section
st.markdown("---")
st.header("📊 Clinical Correlation: Greenery vs. Health")

chart_col, stat_col = st.columns([2, 1])

with chart_col:
    # We use px.scatter for the interactive features
    fig = px.scatter(
        filtered_gdf, 
        x="SIMD2020_Health_Domain_Rank", 
        y="park_density",
        hover_name="Name",
        # Adding more hover data for the 'Bio-Big-Data' feel
        hover_data={
            "SIMD2020_Health_Domain_Rank": True,
            "park_density": ":.2f",
            "park_count": True
        },
        labels={
            "SIMD2020_Health_Domain_Rank": "Health Rank (Higher = Better)",
            "park_density": "Parks per km²"
        },
        trendline="ols", 
        template="plotly_white",
        color="park_density", # Color dots by density for extra visual "pop"
        color_continuous_scale="Viridis"
    )
    
    # Make the plot look professional
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        height=450
    )
    
    st.plotly_chart(fig, use_container_width=True)

with stat_col:
    st.write("### Research Insights")
    correlation = filtered_gdf["SIMD2020_Health_Domain_Rank"].corr(filtered_gdf["park_density"])
    
    # Dynamic interpretation
    st.metric("Pearson Correlation (r)", f"{round(correlation, 3)}")
    
    if correlation > 0.2:
        st.success("✅ **Positive Correlation:** Data suggests a link between greenspace density and improved health outcomes.")
    elif correlation < -0.2:
        st.warning("⚠️ **Inverse Correlation:** This is an unusual finding that warrants deeper clinical investigation.")
    else:
        st.info("ℹ️ **Weak Correlation:** Health outcomes in these zones may be driven more by income or employment than greenery.")

    st.write("#### Top 3 Greenest Zones")
    st.table(filtered_gdf.nlargest(3, 'park_density')[['Name', 'park_density']])




# 5. Correlation Analysis Section
st.markdown("---")
st.header("📊 The Greenery-Health Correlation")

# We use Plotly for the interactive chart
import plotly.express as px

# Create two columns for the chart and the statistical breakdown
chart_col, stat_col = st.columns([2, 1])

with chart_col:
    fig = px.scatter(
        filtered_gdf, 
        x="SIMD2020_Health_Domain_Rank", 
        y="park_density",
        hover_name="Name",
        labels={
            "SIMD2020_Health_Domain_Rank": "Health Rank (Higher = Better)",
            "park_density": "Parks per km²"
        },
        trendline="ols", # Adds the linear regression line
        template="plotly_white",
        color_discrete_sequence=['#2ecc71']
    )
    st.plotly_chart(fig, use_container_width=True)

with stat_col:
    st.write("### Statistical Context")
    # Calculate Pearson Correlation
    correlation = filtered_gdf["SIMD2020_Health_Domain_Rank"].corr(filtered_gdf["park_density"])
    
    st.metric("Correlation Coefficient (r)", f"{round(correlation, 3)}")
    
    st.info("""
    **Interpreting the Trend:**
    * **Positive r:** Suggests areas with more parks have better (higher) health ranks.
    * **Near 0:** Suggests greenspace access isn't a primary driver for health in these specific zones.
    """)
    
    # Showcase your RSE skills: a quick summary of the richest park zones
    st.write("#### Most Diverse Zones")
    top_zones = filtered_gdf.nlargest(3, 'park_count')[['Name', 'park_count']]
    st.dataframe(top_zones, hide_index=True)
