import urllib.request
import os

os.makedirs('data/raw', exist_ok=True)

# These links are direct to the raw data mirrors
files = {
    "data/raw/simd_2020.csv": "https://raw.githubusercontent.com/UrbanBigData/bi-spatial-data-hub/main/data/simd_2020_indicators.csv",
    "data/raw/glasgow_boundaries.json": "https://raw.githubusercontent.com/scotgov/open-data-repository/master/Geography/DataZone2011/Simplified/GlasgowCity.geojson"
}

headers = {'User-Agent': 'Mozilla/5.0'}

for path, url in files.items():
    print(f"Downloading from {url}...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response, open(path, 'wb') as out_file:
            out_file.write(response.read())
        print(f"✅ Saved to {path}")
    except Exception as e:
        print(f"❌ Error downloading: {e}")

# Verification
if os.path.exists('data/raw/simd_2020.csv'):
    with open('data/raw/simd_2020.csv', 'r') as f:
        line = f.readline()
        if "Data_Zone" in line or "DZ" in line:
            print(f"Success! Header found: {line[:50]}...")
        else:
            print("Warning: File exists but content looks like HTML.")
