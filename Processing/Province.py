import os
from pathlib import Path
from typing import List, Dict, Optional

from geopandas import GeoDataFrame

from Processing.GeoObject import GeoObject

from shapely.geometry import Point
from geopy.geocoders import Nominatim
import geopandas as gpd

class Province:
        path: str
        center: Point
        radius: float
        files: List[str]
        gpd: GeoDataFrame
        geo_object_dict: Dict[str, GeoObject]

        def __init__(self, province:str, center: Point, radius: float):
                self.path = f"../data/osm/{province}-latest-free"
                self.center = center
                self.radius = radius
                self.find_files()
                self.geo_object_dict = dict()

        def find_files(self):
                directory = Path(self.path)
                self.files = [file.name for file in directory.iterdir() if file.suffix == '.shp']

        # @staticmethod
        # def find_province(point: Point)->str | None:
        #         geolocator = Nominatim(user_agent="province_locator")
        #         location = geolocator.reverse((point.y, point.x), exactly_one=True, language='en')
        #
        #         if location and 'address' in location.raw:
        #                 province = location.get('state')
        #                 print("Found province : ", province)
        #                 return province
        #         else:
        #                 print("Could not find province")
        #                 return None
        def get_geo_object(self, file):
                if self.geo_object_dict.get(file) is None :
                        self.geo_object_dict[file] = GeoObject(file)

                return self.geo_object_dict[file]

        def find_count(self, file, fclass: Optional[str]) -> int:
                geo_object = self.get_geo_object(file)
                res = geo_object.count_objects(self.center, self.radius, {'fclass': fclass} if fclass else None)
                return res

        def building_count(self):
                return self.find_count(file=f"{self.path}/gis_osm_buildings_a_free_1.shp", fclass=None)
        

def test():
        province = Province('mazowieckie', Point(21.08862, 52.227601), 5000)
        print("Building count = " + str(province.building_count()))

if __name__ == "__main__":
        test()

