import geopandas as gpd
import pandas as pd
import numpy as np
from sklearn.neighbors import KDTree
import math
from shapely import wkt
from shapely.geometry import Point

from Processing.Population import Population
from Processing.Province import Province
from paczkomat import Paczkomaty
from Processing.Province import Province

id_to_woj_bez_znakow = {
    1: 'dolnoslaskie',
    2: 'kujawsko-pomorskie',
    3: 'lubelskie',
    4: 'lubuskie',
    5: 'lodzkie',
    6: 'malopolskie',
    7: 'mazowieckie',
    8: 'opolskie',
    9: 'podkarpackie',
    10: 'podlaskie',
    11: 'pomorskie',
    12: 'slaskie',
    13: 'swietokrzyskie',
    14: 'warminsko-mazurskie',
    15: 'wielkopolskie',
    16: 'zachodniopomorskie'
}

class ScoreCalculator:
    def __init__(self, data_path='data/paczkomaty_processed.csv'):
        self.gdf = pd.read_csv(data_path)
        self.gdf['geometry'] = self.gdf['geometry'].apply(wkt.loads)
        self.gdf = gpd.GeoDataFrame(self.gdf, geometry='geometry')
        self.coords = np.array(list(zip(self.gdf.geometry.x, self.gdf.geometry.y)))
        self.tree = KDTree(self.coords, leaf_size=2)

    def get_residents_count(self, lat, lon, radius_km):
        center = Point(lon, lat)
        return Population().calculate_population(center, radius_km*1000)

    def get_points_in_radius(self, lat, lon, radius_km):
        radius_deg = radius_km / 111.0  # approx km to degrees
        point = np.array([[lon, lat]])
        indices = self.tree.query_radius(point, r=radius_deg, return_distance=False)[0]
        return self.gdf.iloc[indices].copy()

    # def calculate_supply_score(self, residents: float, lockers: int, radius_km: float, alpha: float = 1.0, beta: float = 1.0) -> float:
    #     area_km2 = math.pi * (radius_km ** 2)
    #     return alpha * (lockers / (residents + 1)) + beta * (lockers / (area_km2 + 1))

    def calculate_supply_score(self, residents: float, lockers: int, radius_km: float, alpha: float = 1.0,
                               beta: float = 1.0) -> float:
        area_km2 = math.pi * (radius_km ** 2)
        residents_adj = max(residents, 1)
        lockers_adj = max(lockers, 1)
        score = alpha * (lockers_adj / residents_adj) + beta * (lockers_adj / (area_km2 + 1))
        # optionally take sqrt or log to reduce spread
        score = math.sqrt(score)
        return score

    def _get_nearest_points(self, lon, lat, k=5):
        point = np.array([[lon, lat]])
        distances, indices = self.tree.query(point, k=min(k, len(self.coords)))
        return distances[0], indices[0]

    def _calculate_density_score(self, count, max_count=20):
        normalized = min(count / max_count, 1.0)
        # sigmoid scaling
        return 1 / (1 + math.exp(-10 * (normalized - 0.5)))

    def normalize(self, value, min_val, max_val):
        return (value - min_val) / (max_val - min_val + 1e-6)

    def _calculate_proximity_score(self, distances):
        if len(distances) == 0:
            return 0.0
        weights = np.array([1.0, 0.8, 0.6, 0.4, 0.2])[:len(distances)]
        inv_distances = 1.0 / (1.0 + distances)
        return np.sum(weights * inv_distances) / np.sum(weights)

    def calculate_accessibility_score(self, gdf):
        if len(gdf) == 0:
            return 0.0
        score = 0.0
        count = 0
        if 'location_247' in gdf.columns:
            score += gdf['location_247'].mean()
            count += 1
        elif 'opening_hours' in gdf.columns:
            score += (gdf['opening_hours'] == '24/7').mean()
            count += 1
        if 'easy_access_zone' in gdf.columns:
            score += gdf['easy_access_zone'].mean()
            count += 1
        return score / max(1, count)

    def calculate_demand(self, lat, lon, lockers, radius_km):
        distances, indices = self._get_nearest_points(lon, lat)

        nearest_gdf = self.gdf.iloc[indices]

        density_score = self._calculate_density_score(lockers)
        proximity_score = self._calculate_proximity_score(distances)
        accessibility_score = self.calculate_accessibility_score(nearest_gdf)

        w_density = 1
        w_proximity = 1
        w_accessibility = 1
        w_firmDensity = 1
        w_parkingDensity = 1

        paczkomat = Paczkomaty(csv_path='data/paczkomaty_processed.csv')
        province_id = paczkomat.get_province((lat,lon))
        province_string = id_to_woj_bez_znakow[province_id]
        ObjProv = Province(province_string,Point(lon,lat),radius_km*1000)
        FirmDensity = ObjProv.FirmDensity()
        ParkingDensity = ObjProv.ParkingDensity()
        FirmDensity = self.normalize(FirmDensity, 0, 1000)  # <- dostosuj zakres
        ParkingDensity = self.normalize(ParkingDensity, 0, 500)

        print(f'density_score: {density_score}, proximity_score: {proximity_score}, accessibility_score: {accessibility_score}, firmDensity: {FirmDensity}, parkingDensity: {ParkingDensity}')

        overall_score = (w_density * density_score +
                         w_proximity * proximity_score +
                         w_accessibility * accessibility_score +
                            w_firmDensity * FirmDensity +
                         w_parkingDensity * ParkingDensity)

        return overall_score

    def calculate_result(self, lat, lon, radius_km):
        epsilon = 1e-6
        points_in_radius = self.get_points_in_radius(lat, lon, radius_km)
        lockers = len(points_in_radius)

        residents = self.get_residents_count(lat, lon, radius_km)

        alpha = 1
        beta = 1

        supply_score = self.calculate_supply_score(residents, lockers, radius_km, alpha, beta)
        demand_score = self.calculate_demand(lat, lon, lockers, radius_km)

        print(f'Supply Score: {supply_score:.2f}')
        print(f'Demand Score: {demand_score:.2f}')

        result = min(demand_score / (supply_score + epsilon), 10)
        return result

if __name__ == "__main__":
    calculator = ScoreCalculator()

    lat = 52.2297
    lon = 21.0123
    radius_km = 0.05

    final_score = calculator.calculate_result(lat, lon, radius_km)
    print(f"Final Location Score for radius {radius_km} km: {final_score:.4f}")
