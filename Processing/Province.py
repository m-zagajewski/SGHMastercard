import os
from pathlib import Path
from typing import List, Dict, Optional
import math
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
                self.path = f"data/osm/{province}-latest-free"
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
        def shop_count(self):
                geo_object = self.get_geo_object(f"{self.path}/gis_osm_pois_a_free_1.shp")
                fclasses = [
                        "supermarket",
                        "bakery",
                        "kiosk",
                        "mall",
                        "department_store",
                        "general",
                        "convenience",
                        "clothes",
                        "florist",
                        "chemist",
                        "bookshop",
                        "butcher",
                        "shoe_shop",
                        "beverages",
                        "optician",
                        "jeweller",
                        "gift_shop",
                        "sports_shop",
                        "stationery",
                        "outdoor_shop",
                        "mobile_phone_shop",
                        "toy_shop",
                        "newsagent",
                        "greengrocer",
                        "beauty_shop",
                        "video_shop",
                        "car_dealership",
                        "bicycle_shop",
                        "doityourself",
                        "furniture_shop",
                        "computer_shop",
                        "garden_centre",
                        "hairdresser",
                        "car_repair",
                        "car_rental",
                        "car_wash",
                        "car_sharing",
                        "bicycle_rental",
                        "travel_agent",
                        "laundry",
                        "vending_machine",
                        "vending_cigarette",
                        "vending_parking"
                ]
                return sum(geo_object.count_objects(self.center, self.radius, {'fclass': f}) for f in fclasses)

        def parking_count(self):
                transport_fclasses = [
                        "railway_station",  # Duża stacja kolejowa
                        "railway_halt",  # Mała stacja kolejowa / przystanek
                        "tram_stop",  # Przystanek tramwajowy
                        "bus_stop",  # Przystanek autobusowy
                        "bus_station",  # Dworzec autobusowy
                        "taxi_rank",  # Postój taksówek
                        "airfield",
                        "airport",
                        "taxi_rank"
                ]
                traffic_fclasses = [
                        "fuel",  # Stacja benzynowa
                        "service",  # Miejsce obsługi podróżnych (np. przy autostradach)
                        "parking",  # Parking (ogólny, nieokreślony typ)
                        "parking_site",  # Parking naziemny
                        "parking_multistorey",  # Parking wielopoziomowy
                        "parking_underground",  # Parking podziemny
                        "parking_bicycle"  # Parking rowerowy
                ]
                geo_object = self.get_geo_object(f"{self.path}/gis_osm_transport_a_free_1.shp")
                suma = 0
                suma += sum(geo_object.count_objects(self.center, self.radius, {'fclass': f}) for f in transport_fclasses)
                geo_object2 = self.get_geo_object(f"{self.path}/gis_osm_traffic_a_free_1.shp")
                suma += sum(geo_object2.count_objects(self.center, self.radius, {'fclass': f}) for f in traffic_fclasses)
                return suma

        def business_services_count(self):
                geo_object = self.get_geo_object(f"{self.path}/gis_osm_pois_a_free_1.shp")
                fclasses = [
                        "car_dealership",
                        "car_rental",
                        "car_repair",
                        "car_sharing",
                        "car_wash",
                        "bicycle_rental",
                        "computer_shop",
                        "mobile_phone_shop",
                        "optician",
                        "laundry",
                        "hairdresser",
                        "beauty_shop",
                        "travel_agent",
                        "jeweller",
                        "general",
                        "doityourself",
                        "dry_cleaning",
                        "florist",
                        "butcher",
                        "gift_shop",
                        "sports_shop",
                        "stationery",
                        "outdoor_shop",
                        "video_shop"
                ]
                return sum(geo_object.count_objects(self.center, self.radius, {'fclass': f}) for f in fclasses)

        def health_count(self):
                geo_object = self.get_geo_object(f"{self.path}/gis_osm_pois_a_free_1.shp")
                fclasses = [
                        "hospital",
                        "clinic",
                        "pharmacy",
                        "doctors",
                        "dentist",
                        "veterinary"
                ]
                return sum(geo_object.count_objects(self.center, self.radius, {'fclass': f}) for f in fclasses)

        def education_count(self):
                geo_object = self.get_geo_object(f"{self.path}/gis_osm_pois_a_free_1.shp")
                fclasses = [
                        "school",
                        "kindergarten",
                        "university",
                        "college"
                ]
                return sum(geo_object.count_objects(self.center, self.radius, {'fclass': f}) for f in fclasses)

        def public_safety_count(self):
                geo_object = self.get_geo_object(f"{self.path}/gis_osm_pois_a_free_1.shp")
                fclasses = [
                        "police",
                        "fire_station",
                        "prison",
                        "courthouse",
                        "emergency_phone",
                        "fire_hydrant",
                        "emergency_access"
                ]
                return sum(geo_object.count_objects(self.center, self.radius, {'fclass': f}) for f in fclasses)

        def government_institutions_count(self):
                geo_object = self.get_geo_object(f"{self.path}/gis_osm_pois_a_free_1.shp")
                fclasses = [
                        "town_hall",
                        "embassy",
                        "post_office",
                        "post_box",
                        "community_centre",
                        "public_building"
                ]
                return sum(geo_object.count_objects(self.center, self.radius, {'fclass': f}) for f in fclasses)

        def catering_count(self):
                geo_object = self.get_geo_object(f"{self.path}/gis_osm_pois_a_free_1.shp")
                fclasses = [
                        "restaurant",
                        "cafe",
                        "fast_food",
                        "bar",
                        "pub",
                        "biergarten",
                        "food_court"
                ]
                return sum(geo_object.count_objects(self.center, self.radius, {'fclass': f}) for f in fclasses)

        def tourism_count(self):
                geo_object = self.get_geo_object(f"{self.path}/gis_osm_pois_a_free_1.shp")
                fclasses = [
                        "tourist_info",
                        "tourist_map",
                        "tourist_board",
                        "tourist_guidepost",
                        "viewpoint",
                        "attraction",
                        "picnic_site"
                ]
                return sum(geo_object.count_objects(self.center, self.radius, {'fclass': f}) for f in fclasses)

        def FirmDensity(self):
                res = 0
                res += self.business_services_count()
                res += self.shop_count()
                res = res / (math.pi * (self.radius/1000) ** 2)
                return res

        def ParkingDensity(self):
                res = self.parking_count()
                res = res / (math.pi * (self.radius/1000) ** 2)
                return res

        def ThingsDensity(self):
                res = self.building_count()
                res = res / (math.pi * (self.radius/1000) ** 2)
                return res
#
# def test():
#         province = Province('mazowieckie', Point(20.591443, 52.257846), 2000)
#         print("Building count = " + str(province.building_count()))
#         print("sklep count = " + str(province.shop_count()))
#         print("parking_count = " + str(province.parking_count()))
#
# if __name__ == "__main__":
#         test()
#
