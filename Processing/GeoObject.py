import geopandas as gpd
import pandas as pd
import pyogrio.errors

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

class GeoObject:
        def __init__(self, path):
                try:
                        self.gdf = gpd.read_file(path)
                except pyogrio.errors.DataSourceError:
                        print(f"Could not find file: {path}")
                        exit(0)

                print(self.gdf.head())


def test():     
        GeoObject("../data/osm/mazowieckie-latest-free/gis_osm_buildings_a_free_1.shp")

if __name__ == "__main__":
        test()
        