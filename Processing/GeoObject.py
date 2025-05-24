from typing import Optional, Dict, Any

import geopandas as gpd
import pandas as pd
import pyogrio.errors
import numpy as np

from shapely.geometry import Point

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

class GeoObject:
        gdf: gpd.GeoDataFrame

        def __init__(self, path):
                try:
                        self.gdf = gpd.read_file(path)
                except pyogrio.errors.DataSourceError:
                        print(f"Could not find file: {path}")
                        exit(0)

                # Convert DataFrame to meters notation
                # self.gdf = self.gdf.to_crs(epsg=3857)
                self.process()
                #print(self.gdf.head())

        def process(self):
                self.gdf['center'] = self.gdf['geometry'].centroid

        def count_objects(self, center: Point, radius: float, attr_filters: Optional[Dict[str, Any]] = None) -> int:
                # reference_point = gpd.GeoSeries([center], crs='EPSG:4326').to_crs(self.gdf.crs).iloc[0]
                # self.gdf['distance'] = self.gdf.geometry.distance(reference_point)

                self.gdf['distance'] = GeoObject.haversine(center.x, center.y,
                                                                self.gdf['center'].x, self.gdf['center'].y)

                #print(self.gdf.head())
                filtered_gdf = self.gdf[self.gdf['distance'] <= radius]

                if attr_filters is not None:
                        for key, value in attr_filters.items():
                                filtered_gdf = filtered_gdf[filtered_gdf[key] == value]

                #print("Length: ", len(filtered_gdf))
                #print(filtered_gdf.head())
                #print(filtered_gdf)
                return len(filtered_gdf)

        @staticmethod
        def haversine(lat1, lon1, lat2, lon2):
                R = 6371000  # Earth radius in meters
                phi1 = np.radians(lat1)
                phi2 = np.radians(lat2)
                delta_phi = np.radians(lat2 - lat1)
                delta_lambda = np.radians(lon2 - lon1)

                a = np.sin(delta_phi / 2.0) ** 2 + \
                np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0) ** 2

                c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
                return R * c  # Distance in meters


# def test2():
#         print("licze dla leszna")
#         gobject = GeoObject("../data/osm/mazowieckie-latest-free/gis_osm_pois_a_free_1.shp")
#         center = Point(20.591443, 52.257846)
#         gobject.count_objects(center, 2000)

if __name__ == "__main__":
        test2()