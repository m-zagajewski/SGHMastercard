import geopandas as gpd
import numpy as np
from sklearn.neighbors import KDTree
import pandas as pd
from shapely.geometry import Point

# Załaduj i przetwórz dane (tak jak wcześniej)
df = pd.read_json('data/paczkomaty.json')
df = pd.json_normalize(df.to_dict(orient='records'))
df['geometry'] = df.apply(lambda row: Point(row['location.longitude'], row['location.latitude']), axis=1)
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

def add_density_feature(gdf: gpd.GeoDataFrame, radius: float = 0.01) -> gpd.GeoDataFrame:
    coords = np.array(list(zip(gdf.geometry.x, gdf.geometry.y)))
    tree = KDTree(coords, leaf_size=2)
    counts = tree.query_radius(coords, r=radius, count_only=True)
    gdf['density_1km'] = counts
    return gdf

gdf = add_density_feature(gdf)

# Zapisz do pliku (pickle, ponieważ GeoDataFrame)
gdf.to_pickle('data/paczkomaty_processed.pkl')

print("Dane zostały przetworzone i zapisane do paczkomaty_processed.pkl")
