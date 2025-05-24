import numpy as np
import pandas as pd
import math
from pandas import DataFrame
from geopandas import GeoDataFrame
from pyproj import Transformer
from shapely import wkt, Point

from Processing.GeoObject import GeoObject

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

class Population:
    df: DataFrame

    def __init__(self):
            self.df = pd.read_csv("/Users/michalzagajewski/PycharmProjects/SGHMastercard/data/GRID_NSP2021_RES.csv")
            self.df['geometry'] = self.df['geometry'].apply(wkt.loads)
            self.df = GeoDataFrame(self.df, geometry='geometry')

            self.df = self.df.set_crs('EPSG:2180')  #Dane z GUS
            self.df = self.df.to_crs('EPSG:4326')

            self.df['center'] = self.df['geometry'].centroid

            print(self.df.head())

    @staticmethod
    def convert(lon, lat):

        transformer = Transformer.from_crs("EPSG:4326", "EPSG:3035", always_xy=True)

        easting, northing = transformer.transform(lon, lat)

        # Step 2: Round to nearest 1000
        easting_rounded = int(round(easting, -3))
        northing_rounded = int(round(northing, -3))

        print("Converted: ")
        print(easting_rounded, northing_rounded)
        # Step 3: Format string
        return  f"CRS3035RES1000mN{northing_rounded}E{easting_rounded}"

    @staticmethod
    def get_transformed(lon, lat):
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:2180", always_xy=True)
        easting, northing = transformer.transform(lon, lat)
        return Point(easting, northing)

    def find_containing(self, center: Point, radius: int):
        self.df['distance'] = GeoObject.haversine(center.x, center.y,
                                                   self.df['center'].x, self.df['center'].y)

        # print(self.gdf.head())
        filtered_gdf = self.df[self.df['distance'] <= radius]
        return filtered_gdf

    def calculate_population(self, center: Point, radius: float):
        containing_squares = self.find_containing(center, int(radius))

        if len(containing_squares) == 0:
            return 1000

        circle_area = math.pi * (radius/1000) ** 2
        square_area = 1 * len(containing_squares)

        circle_sum = sum(containing_squares['RES'])
        approximated = (circle_area / square_area) * circle_sum
        return approximated

def test2():
    pop = Population()

    center = Point(20.818511, 52.734613)
    population = pop.calculate_population(center, 2000)
    print(f"Population: {population}")
    # pop.find_containing(center, 1000)

   # Population.convert(51, 21)

if __name__ == "__main__":
    test2()
