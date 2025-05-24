"""
Example script demonstrating the heatmap visualization functionality.

This script shows how to create different types of heatmaps for visualizing
parcel locker data and analysis results.
"""

from parcel_analysis import (
    ScoreCalculator,
    LockerVisualization,
    create_density_heatmap,
    create_score_heatmap,
    create_advanced_score_heatmap
)
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium

def main():
    print("Parcel Locker Heatmap Visualization Examples")
    print("=" * 50)

    # Example 1: Simple density heatmap
    print("\n1. Creating a simple density heatmap...")
    density_map_path = create_density_heatmap()
    print(f"   Density heatmap created at: {density_map_path}")

    # Example 2: Score heatmap with different metrics
    print("\n2. Creating score heatmaps with different metrics...")
    metrics = ['overall_score', 'density_score', 'proximity_score']

    for metric in metrics:
        output_file = f"paczkomaty_{metric}_map.html"
        map_path = create_score_heatmap(metric=metric, output_file=output_file)
        print(f"   {metric.replace('_', ' ').title()} heatmap created at: {map_path}")

    # Example 3: Advanced score heatmap
    print("\n3. Creating an advanced score heatmap...")
    advanced_map_path = create_advanced_score_heatmap()
    print(f"   Advanced score heatmap created at: {advanced_map_path}")

    # Example 4: Custom heatmap with specific bounds and grid size
    print("\n4. Creating a custom heatmap...")

    # Initialize calculator
    calculator = ScoreCalculator()

    # Define custom bounds (Kraków area)
    krakow_bounds = {
        'lat_min': 50.00,
        'lat_max': 50.10,
        'lon_min': 19.90,
        'lon_max': 20.10
    }

    # Create base map centered on Kraków
    m = LockerVisualization.create_base_map(
        center=[(krakow_bounds['lat_min'] + krakow_bounds['lat_max']) / 2,
                (krakow_bounds['lon_min'] + krakow_bounds['lon_max']) / 2],
        zoom_start=12
    )

    # Add a heatmap layer
    m = LockerVisualization.create_grid_heatmap(
        calculator=calculator,
        bounds=krakow_bounds,
        grid_size=20,  # Lower grid size for faster computation
        metric='density_score',
        map_obj=m
    )

    # Save the map
    custom_map_path = LockerVisualization.save_map(m, 'krakow_density_heatmap.html')
    print(f"   Custom heatmap created at: {custom_map_path}")

    # Example 5: Combined visualization (markers + heatmap)
    print("\n5. Creating a combined visualization (markers + heatmap)...")

    # Load data
    df = pd.read_json('data/paczkomaty.json')
    df = pd.json_normalize(df.to_dict(orient='records'))
    df['geometry'] = df.apply(lambda row: Point(row['location.longitude'], row['location.latitude']), axis=1)
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

    # Filter to Warsaw area
    warsaw_bounds = {
        'lat_min': 52.15,
        'lat_max': 52.30,
        'lon_min': 20.90,
        'lon_max': 21.10
    }

    warsaw_gdf = gdf[
        (gdf.geometry.y >= warsaw_bounds['lat_min']) &
        (gdf.geometry.y <= warsaw_bounds['lat_max']) &
        (gdf.geometry.x >= warsaw_bounds['lon_min']) &
        (gdf.geometry.x <= warsaw_bounds['lon_max'])
    ]

    # Create base map
    m = LockerVisualization.create_base_map(
        center=[(warsaw_bounds['lat_min'] + warsaw_bounds['lat_max']) / 2,
                (warsaw_bounds['lon_min'] + warsaw_bounds['lon_max']) / 2],
        zoom_start=12
    )

    # Add markers
    m = LockerVisualization.create_marker_map(
        gdf=warsaw_gdf,
        popup_col='name',
        map_obj=m,
        cluster=True
    )

    # Add heatmap layer
    m = LockerVisualization.create_heatmap(
        gdf=warsaw_gdf,
        value_col='density_1km' if 'density_1km' in warsaw_gdf.columns else None,
        map_obj=m,
        radius=15,
        blur=10
    )

    # Add layer control
    folium.LayerControl().add_to(m)

    # Save the map
    combined_map_path = LockerVisualization.save_map(m, 'warsaw_combined_map.html')
    print(f"   Combined visualization created at: {combined_map_path}")

    print("\nAll visualizations have been created successfully!")
    print("Open the HTML files in a web browser to view the interactive maps.")

if __name__ == "__main__":
    main()
