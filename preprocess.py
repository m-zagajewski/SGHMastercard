import geopandas as gpd
import numpy as np
from sklearn.neighbors import KDTree
import pandas as pd
from shapely.geometry import Point

possible_functions = [
    "Send and collect standard parcel",
    "Standard parcel send",
    "Standard parcel collect",
    "Standard parcel reverse return to sender",
    "Standard letter collect",
    "Standard letter send",
    "Allegro parcel collect",
    "Allegro parcel send",
    "Allegro parcel return to sender",
    "Allegro letter collect",
    "Allegro letter send",
    "Allegro letter return to sender",
    "Allegro courier parcel collect",
    "Allegro courier parcel send",
    "Allegro courier parcel return to sender",
    "Courier parcel collect",
    "Courier parcel send",
    "Courier parcel return to sender",
    "Send and collect baggage from machine on airport",
    "Send and collect baggage from machine outside of airport",
    "Reservation collect from cooling machine",
    "Send and collect laundry",
    "Avizo collect"
]

def load_raw_data(file_path='data/paczkomaty.json'):
    df = pd.read_json(file_path)
    df = pd.json_normalize(df.to_dict(orient='records'))
    # Usuń dane bez lokalizacji
    df = df[~((df['location.latitude'] == 0) & (df['location.longitude'] == 0))]
    # Usuń niepotrzebne kolumny
    columns_to_drop = ['href', 'payment_point_descr', 'apm_doubled', 'physical_type_description', 'address.line2','location_date', 'location_description', 'location_description_1', 'location_description_2', 'distance', 'phone_number', 'partner_id', 'image_url', 'address.line1', 'address_details.city', 'address_details.post_code', 'address_details.street', 'address_details.building_number', 'address_details.flat_number', 'operating_hours_extended.customer', 'operating_hours_extended.customer.monday', 'operating_hours_extended.customer.tuesday', 'operating_hours_extended.customer.wednesday', 'operating_hours_extended.customer.thursday', 'operating_hours_extended.customer.friday', 'operating_hours_extended.customer.saturday', 'operating_hours_extended.customer.sunday', 'payment_type.1', 'payment_type.2', 'payment_type.3', 'operating_hours_extended']
    df = df.drop(columns=columns_to_drop, errors='ignore')
    return df

def create_geodataframe(df):
    df['geometry'] = df.apply(
        lambda row: Point(row['location.longitude'], row['location.latitude']) 
        if 'location.longitude' in row and 'location.latitude' in row 
        else None, 
        axis=1
    )

    df = df.dropna(subset=['geometry'])
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

    return gdf

def add_density_feature(gdf, radius=0.01):
    coords = np.array(list(zip(gdf.geometry.x, gdf.geometry.y)))
    tree = KDTree(coords, leaf_size=2)
    counts = tree.query_radius(coords, r=radius, count_only=True)
    gdf['density_1km'] = counts
    return gdf

def add_functions_features(gdf):
    """
    Dla każdej możliwej funkcji tworzy kolumnę 0/1 oraz oblicza score jako stosunek liczby
    dostępnych funkcji do maksymalnej liczby funkcji.
    """
    # One-hot encoding funkcji
    for func in possible_functions:
        gdf[f'func_{func}'] = gdf['functions'].apply(lambda x: int(func in x) if isinstance(x, list) else 0)
    gdf['functions_count'] = gdf['functions'].apply(lambda x: len(x) if isinstance(x, list) else 0)
    max_funcs = len(possible_functions)
    gdf['functions_score'] = gdf['functions_count'] / max_funcs
    for func in possible_functions:
        gdf.drop(columns=[f'func_{func}'], inplace=True)
    gdf.drop(columns=['functions'], inplace=True)
    return gdf

def map_woje(gdf):
    wojewodztwa_map = {
        'dolnośląskie': 1,
        'kujawsko-pomorskie': 2,
        'lubelskie': 3,
        'lubuskie': 4,
        'łódzkie': 5,
        'małopolskie': 6,
        'mazowieckie': 7,
        'opolskie': 8,
        'podkarpackie': 9,
        'podlaskie': 10,
        'pomorskie': 11,
        'śląskie': 12,
        'świętokrzyskie': 13,
        'warmińsko-mazurskie': 14,
        'wielkopolskie': 15,
        'zachodniopomorskie': 16
    }
    salary_map = {
        1: 7287.68,
        2: 6914.37,
        3: 6753.32,
        4: 7014.21,
        5: 6962.86,
        6: 7287.18,
        7: 8466.61,
        8: 6884.62,
        9: 6865.01,
        10: 6822.38,
        11: 7583.36,
        12: 7567.01,
        13: 6807.54,
        14: 6911.83,
        15: 7334.48,
        16: 7082.56
    }

    # Mapujemy i konwertujemy na int (z pominięciem NaN)
    gdf['wojewodztwo_id'] = gdf['address_details.province'].str.lower().map(wojewodztwa_map)
    gdf['wojewodztwo_id'] = gdf['wojewodztwo_id'].fillna(0).astype(int)

    gdf['average_salary'] = gdf['wojewodztwo_id'].map(salary_map)
    gdf.drop(columns=['address_details.province'], inplace=True)
    return gdf


def preprocess_data(input_file='data/paczkomaty.json', output_file='data/paczkomaty_processed.csv'):
    df = load_raw_data(input_file)
    gdf = create_geodataframe(df)
    gdf = add_density_feature(gdf)
    gdf = add_functions_features(gdf)
    gdf = map_woje(gdf)
    gdf.to_csv(output_file)
    print(f"Data processed and saved to {output_file}")
    return gdf


if __name__ == "__main__":
    preprocess_data()
