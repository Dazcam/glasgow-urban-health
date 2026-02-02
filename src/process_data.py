import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon
import json

def osm_json_to_gdf(json_data):
    """Converts raw OSM JSON (nodes/ways) to a GeoDataFrame."""
    nodes = {n['id']: (n['lon'], n['lat']) for n in json_data['elements'] if n['type'] == 'node'}
    geoms = []
    for el in json_data['elements']:
        if el['type'] == 'way':
            coords = [nodes[node_id] for node_id in el['nodes']]
            if len(coords) >= 3:
                geoms.append(Polygon(coords))
    return gpd.GeoDataFrame(geometry=geoms, crs="EPSG:4326")

def run_pipeline():
    # 1. Load SIMD Data first (we'll use this as our filter key)
    print("Loading SIMD master list...")
    simd = pd.read_csv('data/raw/simd2020_withgeog/simd2020_withinds.csv')
    
    # Identify Glasgow DataZones from the SIMD file
    glasgow_ids = simd[simd['Council_area'].str.contains('Glasgow', na=False)]['Data_Zone'].unique()
    print(f"Targeting {len(glasgow_ids)} Glasgow DataZones based on SIMD records.")

    # 2. Load Boundaries
    print("Loading boundaries...")
    zones = gpd.read_file('data/raw/SG_DataZoneBdry_2011/SG_DataZone_Bdry_2011.shp')
    
    # Filter the shapefile using the IDs from our SIMD master list
    # Then project to British National Grid (meters) for accurate math
    glasgow_zones = zones[zones['DataZone'].isin(glasgow_ids)].to_crs(epsg=27700)
    
    # Calculate land area in square kilometers
    glasgow_zones['area_km2'] = glasgow_zones.geometry.area / 1_000_000

    # 3. Process Greenspace
    print("Processing Greenspace...")
    with open('data/raw/glasgow_greenspace.json') as f:
        osm_data = json.load(f)
    
    # Ensure parks are also in British National Grid for the spatial join
    # (Assuming osm_json_to_gdf is defined in your script)
    parks_gdf = osm_json_to_gdf(osm_data).set_crs(epsg=4326).to_crs(epsg=27700)

    # 4. Spatial Join (The core analytics)
    print("Performing Spatial Join...")
    # 'left' join ensures we keep all Glasgow zones, even those with 0 parks
    joined = gpd.sjoin(glasgow_zones, parks_gdf, how="left", predicate="intersects")
    
    # Count parks and handle zones with zero matches
    park_counts = joined.groupby('DataZone').size().reset_index(name='park_count')
    
    # 5. Final Merge
    print("Merging datasets...")
    # Merge health data and park counts back into the spatial zones
    final = glasgow_zones.merge(simd, left_on='DataZone', right_on='Data_Zone')
    final = final.merge(park_counts, on='DataZone')

    # 6. Calculate Metrics
    final['park_density'] = final['park_count'] / final['area_km2']
    
    # 7. Export for Visualization (Convert back to Lat/Lon for the web)
    print("Exporting to GeoJSON...")
    final.to_crs(epsg=4326).to_file('data/processed/dashboard_data.geojson', driver='GeoJSON')
    
    print(f"✅ Pipeline complete! Processed {len(final)} DataZones.")

if __name__ == "__main__":
    run_pipeline()


