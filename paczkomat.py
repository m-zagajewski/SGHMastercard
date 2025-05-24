import csv
from math import radians, cos, sin, asin, sqrt
from typing import List, Tuple


class Paczkomaty:
    def __init__(self, csv_path: str):
        self.data = []  # List of (id, name, lon, lat)
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            print(reader.fieldnames)
            for row in reader:
                try:
                    lat = float(row["location.latitude"])
                    lon = float(row["location.longitude"])
                    self.data.append({
                        "id": row["id"],
                        "name": row["name"],
                        "lat": lat,
                        "lon": lon,
                        "wojewodztwo_id": row["wojewodztwo_id"],
                    })
                except Exception as e:
                    continue  # Skip rows with bad data

    def _haversine(self, lon1, lat1, lon2, lat2):
        R = 6371.0  # Earth radius in km
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        return R * c

    def get_nearby(self, center: Tuple[float, float], radius_km: float) -> List[dict]:
        lat0, lon0 = center
        print(self.data)
        return [
            p for p in self.data
            if self._haversine(lon0, lat0, p["lon"], p["lat"]) <= radius_km
        ]

    def get_province(self, center: Tuple[float, float]) -> int:
        min_distance = 999999
        lat0, lon0 = center
        result = None
        for p in self.data:
            distance = self._haversine(lon0, lat0, p["lon"], p["lat"])
            if distance < min_distance:
                min_distance = distance
                result = p["wojewodztwo_id"]
        return int(float(result))