#!/bin/bash

# SIMD 2020 Indicator Data (Direct CSV link)
# This includes the 'Health' column we need
echo "Downloading SIMD Health Data..."
curl -L -o data/raw/simd_2020_indicators.csv "https://www.gov.scot/binaries/content/documents/govscot/publications/statistics/2020/01/scottish-index-of-multiple-deprivation-2020-indicator-data/documents/simd-2020-indicator-data/simd-2020-indicator-data/govscot%3Adocument/SIMD%2B2020%2B-%2Bindicator%2Bdata.csv"

# Glasgow Data Zone Boundaries (GeoJSON)
# Note: For the dashboard to be 'lightweight', we use the simplified boundaries.
echo "Downloading Glasgow Boundary GeoJSON..."
curl -L -o data/raw/glasgow_boundaries.json "https://raw.githubusercontent.com/scotgov/open-data-repository/master/Geography/DataZone2011/Simplified/GlasgowCity.geojson"

echo "Data download complete. Check data/raw/ folder."
