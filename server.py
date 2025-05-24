from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from paczkomat import Paczkomaty
from score_calculator import ScoreCalculator
from Processing.Province import Province
from shapely.geometry import Point

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
app = FastAPI()
paczkomaty = Paczkomaty("./data/paczkomaty_processed.csv")

# Allow frontend to fetch
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/paczkomaty")
def get_paczkomaty(
    lat: float = Query(...),
    lon: float = Query(...),
    radius: float = Query(2.0)  # in km
) -> List[dict]:
    return paczkomaty.get_nearby((lat, lon), radius)

@app.get("/api/obszar")
def get_obszar(
        lat: float = Query(...),
        lon: float = Query(...),
        radius: float = Query(...)  # in meters
) -> dict:
    calculator = ScoreCalculator()
    radiusKM = radius / 1000
    score = calculator.calculate_result(lat, lon, radiusKM)
    population = calculator.get_residents_count(lat, lon, radiusKM)
    result = {}
    province_id = paczkomaty.get_province((lat, lon))
    print("Lon: ", lon, "Lat: ", lat, "Radius: ", radius)
    provinceString = id_to_woj_bez_znakow[province_id]
    print("PROVINCE: ", provinceString)
    provinceObject = Province(provinceString, Point(lon,lat), radius)

    result['shopCount'] = provinceObject.shop_count()
    result['building'] = provinceObject.building_count()
    result['parking'] = provinceObject.parking_count()
    result['buissness'] = provinceObject.business_services_count()
    result['health'] = provinceObject.health_count()
    result['education'] = provinceObject.education_count()
    result['public_safety'] = provinceObject.public_safety_count()
    result['goverment_institutions'] = provinceObject.government_institutions_count()
    result['catering'] = provinceObject.catering_count()
    result['tourism'] = provinceObject.tourism_count()
    result['population'] = population


    # result[]
    result['score'] = score
    return result