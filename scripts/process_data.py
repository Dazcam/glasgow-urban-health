import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon

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
    # 1. Load Boundaries (Using relative path inside bound container)
    print("Loading boundaries...")
    zones = gpd.read_file('data/raw/SG_DataZoneBdry_2011/SG_DataZone_Bdry_2011.shp')
    
    # Filter for Glasgow (Checking 'Name' column)
    glasgow_zones = zones[zones['Name'].str.contains('Glasgow', na=False)].to_crs(epsg=4326)

    # 2. Load SIMD Data
    print("Loading SIMD...")
    simd = pd.read_csv('data/raw/simd2020_withgeog/simd2020_withinds.csv')
    
    # 3. Process Greenspace
    print("Processing Greenspace...")
    import json
    with open('data/raw/glasgow_greenspace.json') as f:
        osm_data = json.load(f)
    parks_gdf = osm_json_to_gdf(osm_data)

    # 4. Spatial Join (The core analytics)
    # Count parks that intersect each Data Zone
    joined = gpd.sjoin(glasgow_zones, parks_gdf, how="left", predicate="intersects")
    park_counts = joined.groupby('DataZone').size().reset_index(name='park_count')
    
    # 5. Final Merge
    final = glasgow_zones.merge(simd, left_on='DataZone', right_on='Data_Zone')
    final = final.merge(park_counts, on='DataZone')

    # Save to Processed
    final.to_file('data/processed/dashboard_data.geojson', driver='GeoJSON')
    print("✅ Pipeline complete! File saved to data/processed/dashboard_data.geojson")

if __name__ == "__main__":
    run_pipeline()
