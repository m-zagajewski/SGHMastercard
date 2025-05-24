import pandas as pd
from shapely.geometry import Point
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster

# 1. Load JSON file directly using pandas (no json lib)
df = pd.read_json('data/paczkomaty.json')

# 2. Flatten nested location dictionary into columns (if needed)
df = pd.json_normalize(df.to_dict(orient='records'))

# 3. Create geometry column from longitude and latitude
df['geometry'] = df.apply(lambda row: Point(row['location.longitude'], row['location.latitude']), axis=1)

# 4. Ensure 'name' column exists, fill missing with empty string
if 'name' not in df.columns:
    df['name'] = ''
else:
    df['name'] = df['name'].fillna('')

# 5. Convert to GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

# 6. Create Folium map
m = folium.Map(location=[52.0, 19.0], zoom_start=6, tiles="CartoDB positron")

# 7. Add MarkerCluster
marker_cluster = MarkerCluster().add_to(m)
for idx, row in gdf.iterrows():
    folium.Marker(
        location=[row.geometry.y, row.geometry.x],
        popup=row['name'],
        icon=folium.Icon(color='red', icon='cube', prefix='fa')
    ).add_to(marker_cluster)

# 8. Save and/or display
m.save('paczkomaty_map.html')
m
