import pandas as pd
import geopandas as gpd
import json
from shapely.geometry import Point

def run_pipeline():
    print("Preprocessing data ...")
    
    # 1. Load
    simd = pd.read_csv('data/raw/simd2020_withgeog/simd2020_withinds.csv')
    zones = gpd.read_file('data/raw/SG_DataZoneBdry_2011/SG_DataZone_Bdry_2011.shp')
    with open('data/raw/glasgow_greenspace.json') as f:
        osm_data = json.load(f)
    with open('data/processed/indicator_metadata.json') as f:
        metadata = json.load(f)

    # 2. Filter & Project
    glasgow_ids = simd[simd['Council_area'].str.contains('Glasgow', na=False)]['Data_Zone'].unique()
    glasgow_zones = zones[zones['DataZone'].isin(glasgow_ids)].to_crs(epsg=27700)

    # 3. Spatial Join
    points = [Point(el['lon'], el['lat']) for el in osm_data['elements'] if 'lat' in el]
    parks_gdf = gpd.GeoDataFrame(geometry=points, crs="EPSG:4326").to_crs(epsg=27700)
    
    joined = gpd.sjoin(glasgow_zones, parks_gdf, how="left", predicate="intersects")
    park_counts = joined.groupby('DataZone').size().reset_index(name='park_count')

    # 4. Merge & "Bake" Metrics
    final = glasgow_zones.merge(park_counts, on='DataZone').merge(simd, left_on='DataZone', right_on='Data_Zone')
    final['area_km2'] = final.geometry.area / 1_000_000
    final['park_density'] = final['park_count'] / final['area_km2']

    # 5. Clean NAs (Impute with Median)
    for col in metadata['indicators']:
        if final[col].isna().any():
            final[col] = final[col].fillna(final[col].median())

    # 6. Export to Parquet (High Speed)
    final.to_crs(epsg=4326).to_parquet('data/processed/dashboard_data.parquet')
    print("✅ High-performance Parquet baked.")

if __name__ == "__main__":
    run_pipeline()
