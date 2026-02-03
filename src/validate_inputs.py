import pandas as pd
import geopandas as gpd
import json
import sys
from shapely.geometry import Point

def validate_data():
    print("🚀 Starting Comprehensive Data Validation...")
    errors = 0
    
    # --- 1. Robust SIMD Check ---
    try:
        simd = pd.read_csv('data/raw/simd2020_withgeog/simd2020_withinds.csv')
        
        # Dynamic Column Discovery
        exclude_list = ['Data_Zone', 'Intermediate_Zone', 'Council_area', 'City', 'DZ', 'Easting', 'Northing']
        numeric_cols = simd.select_dtypes(include=['number']).columns.tolist()
        analysis_cols = [c for c in numeric_cols if c not in exclude_list]
        
        print(f"✅ SIMD CSV: Loaded. Found {len(analysis_cols)} dynamic indicators.")
        
        # Check for NAs in these dynamic columns
        null_summary = simd[analysis_cols].isna().sum()
        if null_summary.sum() > 0:
            print(f"⚠️  SIMD CSV: Found {null_summary.sum()} missing values across indicators.")
            
        # Ensure the 'Join Key' exists
        if 'Data_Zone' not in simd.columns:
            print("❌ SIMD CSV: Missing 'Data_Zone' join key!")
            errors += 1
            
    except Exception as e:
        print(f"❌ SIMD CSV: Load failed: {e}")
        errors += 1

    # --- 2. Spatial Integrity Check (Restored functionality) ---
    try:
        zones = gpd.read_file('data/raw/SG_DataZoneBdry_2011/SG_DataZone_Bdry_2011.shp')
        print(f"✅ Shapefile: Loaded {len(zones)} features.")
        
        # CRITICAL: CRS Check (Ensures spatial joins work tomorrow)
        if zones.crs != "EPSG:27700":
            print(f"⚠️  Shapefile: CRS is {zones.crs}, expected EPSG:27700 (meters).")
            
        if 'DataZone' not in zones.columns:
            print("❌ Shapefile: Missing 'DataZone' attribute column!")
            errors += 1
    except Exception as e:
        print(f"❌ Shapefile: Load failed: {e}")
        errors += 1

    # --- 3. OSM JSON Check (Restored functionality) ---
    try:
        with open('data/raw/glasgow_greenspace.json') as f:
            osm = json.load(f)
        elements = osm.get('elements', [])
        if not elements:
            print("❌ OSM JSON: No 'elements' found in JSON.")
            errors += 1
        else:
            print(f"✅ OSM JSON: Found {len(elements)} raw features.")
    except Exception as e:
        print(f"❌ OSM JSON: Load failed: {e}")
        errors += 1

    # --- 4. Export Metadata for the App ---
    if errors == 0:
        # We save the list of columns so the App knows what to put in the dropdown
        metadata = {
            "indicators": analysis_cols,
            "total_zones": len(zones),
            "osm_features": len(elements)
        }
        with open('data/processed/indicator_metadata.json', 'w') as f:
            json.dump(metadata, f)
        print("\n✨ ALL CHECKS PASSED. Metadata exported for Dashboard.")
    else:
        print(f"\n🛑 Validation failed with {errors} errors. Fix before running pipeline.")
        sys.exit(1)

if __name__ == "__main__":
    validate_data()
