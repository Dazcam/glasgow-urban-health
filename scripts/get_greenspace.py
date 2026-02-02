import requests
import json
import os

def fetch_glasgow_greenspace():
    print("🛰️ Querying OpenStreetMap for Glasgow Greenspace...")
    
    # Overpass API Query: Find all leisure=park or landuse=grass within Glasgow city bounds
    # The bounding box [55.77, -4.43, 55.95, -4.08] covers the Glasgow council area
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = """
    [out:json][timeout:25];
    (
      way["leisure"="park"](55.77,-4.43,55.95,-4.08);
      way["landuse"="grass"](55.77,-4.43,55.95,-4.08);
      way["leisure"="garden"](55.77,-4.43,55.95,-4.08);
      relation["leisure"="park"](55.77,-4.43,55.95,-4.08);
    );
    out body;
    >;
    out skel qt;
    """
    
    response = requests.post(overpass_url, data={'data': overpass_query})
    
    if response.status_code == 200:
        os.makedirs('data/raw', exist_ok=True)
        with open('data/raw/glasgow_greenspace.json', 'w') as f:
            json.dump(response.json(), f)
        print("✅ Success! Greenspace data saved to data/raw/glasgow_greenspace.json")
    else:
        print(f"❌ Failed to query OSM. Status code: {response.status_code}")

if __name__ == "__main__":
    fetch_glasgow_greenspace()
