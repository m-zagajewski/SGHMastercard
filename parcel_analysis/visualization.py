"""
Visualization functionality for parcel locker analysis.

This module provides methods for visualizing parcel locker data, including
heatmaps and other geospatial visualizations.
"""

import folium
from folium.plugins import HeatMap, MarkerCluster
import geopandas as gpd
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
import branca.colormap as cm

class LockerVisualization:
    """
    A class providing visualization methods for parcel lockers.

    This class contains methods to create various visualizations of parcel locker data,
    including heatmaps, marker maps, and choropleth maps.
    """

    @staticmethod
    def create_base_map(center: List[float] = [52.0, 19.0], zoom_start: int = 6, 
                       tiles: str = "CartoDB positron") -> folium.Map:
        """
        Create a base folium map.

        Args:
            center (List[float]): Center coordinates [lat, lon] for the map.
            zoom_start (int): Initial zoom level.
            tiles (str): Map tile style.

        Returns:
            folium.Map: A folium map object.
        """
        return folium.Map(location=center, zoom_start=zoom_start, tiles=tiles)

    @staticmethod
    def create_marker_map(gdf: gpd.GeoDataFrame, popup_col: str = 'name',
                         map_obj: Optional[folium.Map] = None,
                         cluster: bool = True) -> folium.Map:
        """
        Create a map with markers for each parcel locker.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame containing parcel locker data.
            popup_col (str): Column to use for marker popups.
            map_obj (folium.Map, optional): Existing map to add markers to.
            cluster (bool): Whether to cluster markers.

        Returns:
            folium.Map: A folium map with markers.
        """
        # Create map if not provided
        if map_obj is None:
            map_obj = LockerVisualization.create_base_map()

        # Ensure popup column exists
        if popup_col not in gdf.columns:
            popup_col = gdf.columns[0]  # Use first column as fallback

        # Add markers
        if cluster:
            marker_cluster = MarkerCluster().add_to(map_obj)
            for idx, row in gdf.iterrows():
                folium.Marker(
                    location=[row.geometry.y, row.geometry.x],
                    popup=str(row[popup_col]),
                    icon=folium.Icon(color='red', icon='cube', prefix='fa')
                ).add_to(marker_cluster)
        else:
            for idx, row in gdf.iterrows():
                folium.Marker(
                    location=[row.geometry.y, row.geometry.x],
                    popup=str(row[popup_col]),
                    icon=folium.Icon(color='red', icon='cube', prefix='fa')
                ).add_to(map_obj)

        return map_obj

    @staticmethod
    def create_heatmap(gdf: gpd.GeoDataFrame, 
                      value_col: Optional[str] = None,
                      map_obj: Optional[folium.Map] = None,
                      radius: int = 15,
                      blur: int = 10,
                      gradient: Optional[Dict[float, str]] = None,
                      min_opacity: float = 0.2,
                      max_zoom: int = 18) -> folium.Map:
        """
        Create a heatmap of parcel locker density or other metrics.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame containing parcel locker data.
            value_col (str, optional): Column to use for heatmap intensity values.
                                      If None, all points have equal weight.
            map_obj (folium.Map, optional): Existing map to add heatmap to.
            radius (int): Radius of each point in the heatmap.
            blur (int): Amount of blur in the heatmap.
            gradient (Dict[float, str], optional): Color gradient for the heatmap.
            min_opacity (float): Minimum opacity of the heatmap.
            max_zoom (int): Maximum zoom level for the heatmap.

        Returns:
            folium.Map: A folium map with heatmap.
        """
        # Create map if not provided
        if map_obj is None:
            map_obj = LockerVisualization.create_base_map()

        # Prepare data for heatmap
        if value_col is not None and value_col in gdf.columns:
            # Use specified column for intensity values
            heat_data = [[row.geometry.y, row.geometry.x, row[value_col]] 
                         for idx, row in gdf.iterrows() if pd.notnull(row[value_col])]
        else:
            # All points have equal weight
            heat_data = [[row.geometry.y, row.geometry.x, 1.0] 
                         for idx, row in gdf.iterrows()]

        # Default gradient if not provided
        if gradient is None:
            gradient = {
                0.0: 'blue',
                0.25: 'green',
                0.5: 'yellow',
                0.75: 'orange',
                1.0: 'red'
            }

        # Add heatmap to map
        HeatMap(
            heat_data,
            radius=radius,
            blur=blur,
            gradient=gradient,
            min_opacity=min_opacity,
            max_zoom=max_zoom
        ).add_to(map_obj)

        return map_obj

    @staticmethod
    def create_grid_heatmap(calculator, bounds: Dict[str, float], 
                           grid_size: int = 50,
                           metric: str = 'overall_score',
                           radius: float = 0.01,
                           map_obj: Optional[folium.Map] = None) -> folium.Map:
        """
        Create a heatmap by calculating scores on a grid of points.

        Args:
            calculator: An instance of ScoreCalculator to calculate scores.
            bounds (Dict[str, float]): Bounding box with 'lat_min', 'lat_max', 'lon_min', 'lon_max'.
            grid_size (int): Number of points in each dimension of the grid.
            metric (str): Metric to visualize ('overall_score', 'density_score', 'proximity_score', etc.).
            radius (float): Radius in degrees to consider for each point.
            map_obj (folium.Map, optional): Existing map to add heatmap to.

        Returns:
            folium.Map: A folium map with heatmap.
        """
        # Create map if not provided
        if map_obj is None:
            center_lat = (bounds['lat_min'] + bounds['lat_max']) / 2
            center_lon = (bounds['lon_min'] + bounds['lon_max']) / 2
            map_obj = LockerVisualization.create_base_map([center_lat, center_lon], zoom_start=10)

        # Calculate lat/lon steps
        lat_step = (bounds['lat_max'] - bounds['lat_min']) / (grid_size - 1) if grid_size > 1 else 0
        lon_step = (bounds['lon_max'] - bounds['lon_min']) / (grid_size - 1) if grid_size > 1 else 0

        # Generate grid points and calculate scores
        heat_data = []
        for i in range(grid_size):
            for j in range(grid_size):
                lat = bounds['lat_min'] + i * lat_step
                lon = bounds['lon_min'] + j * lon_step

                # Calculate score
                try:
                    score_result = calculator.calculate_score(lat, lon, radius)
                    if metric in score_result:
                        value = score_result[metric]
                        heat_data.append([lat, lon, value])
                except Exception as e:
                    # Skip points that cause errors
                    continue

        # Add heatmap to map
        HeatMap(
            heat_data,
            radius=15,
            blur=10,
            min_opacity=0.2,
            max_zoom=18
        ).add_to(map_obj)

        # Add a legend
        colormap = cm.LinearColormap(
            ['blue', 'green', 'yellow', 'orange', 'red'],
            vmin=0, vmax=1,
            caption=f'Parcel Locker {metric.replace("_", " ").title()}'
        )
        colormap.add_to(map_obj)

        return map_obj

    @staticmethod
    def create_advanced_heatmap(calculator, bounds: Dict[str, float], 
                              grid_size: int = 50,
                              map_obj: Optional[folium.Map] = None) -> folium.Map:
        """
        Create a heatmap using advanced scores (including accessibility and functionality).

        Args:
            calculator: An instance of ScoreCalculator to calculate scores.
            bounds (Dict[str, float]): Bounding box with 'lat_min', 'lat_max', 'lon_min', 'lon_max'.
            grid_size (int): Number of points in each dimension of the grid.
            map_obj (folium.Map, optional): Existing map to add heatmap to.

        Returns:
            folium.Map: A folium map with heatmap.
        """
        from parcel_analysis.analysis import LockerAnalysis

        # Create map if not provided
        if map_obj is None:
            center_lat = (bounds['lat_min'] + bounds['lat_max']) / 2
            center_lon = (bounds['lon_min'] + bounds['lon_max']) / 2
            map_obj = LockerVisualization.create_base_map([center_lat, center_lon], zoom_start=10)

        # Calculate lat/lon steps
        lat_step = (bounds['lat_max'] - bounds['lat_min']) / (grid_size - 1) if grid_size > 1 else 0
        lon_step = (bounds['lon_max'] - bounds['lon_min']) / (grid_size - 1) if grid_size > 1 else 0

        # Generate grid points and calculate scores
        heat_data = []
        for i in range(grid_size):
            for j in range(grid_size):
                lat = bounds['lat_min'] + i * lat_step
                lon = bounds['lon_min'] + j * lon_step

                try:
                    # Calculate basic score
                    basic_score = calculator.calculate_score(lat, lon, 0.01)

                    # Get points in radius
                    points = calculator.get_points_in_radius(lat, lon, 0.01)

                    # Calculate advanced scores
                    accessibility = LockerAnalysis.calculate_accessibility_score(points)
                    functionality = LockerAnalysis.calculate_functionality_score(points)

                    # Create advanced score
                    advanced_score = LockerAnalysis.calculate_advanced_score(
                        basic_score, accessibility, functionality
                    )

                    # Use overall score for heatmap
                    value = advanced_score['overall_score']
                    heat_data.append([lat, lon, value])
                except Exception as e:
                    # Skip points that cause errors
                    continue

        # Add heatmap to map
        HeatMap(
            heat_data,
            radius=15,
            blur=10,
            min_opacity=0.2,
            max_zoom=18
        ).add_to(map_obj)

        # Add a legend
        colormap = cm.LinearColormap(
            ['blue', 'green', 'yellow', 'orange', 'red'],
            vmin=0, vmax=1,
            caption='Parcel Locker Advanced Score'
        )
        colormap.add_to(map_obj)

        return map_obj

    @staticmethod
    def save_map(map_obj: folium.Map, output_file: str = 'parcel_locker_heatmap.html') -> str:
        """
        Save a folium map to an HTML file.

        Args:
            map_obj (folium.Map): Folium map to save.
            output_file (str): Output file path.

        Returns:
            str: Path to the saved file.
        """
        map_obj.save(output_file)
        return output_file

def create_density_heatmap(output_file: str = 'paczkomaty_density_map.html') -> str:
    """
    Create a heatmap of parcel locker density.

    Args:
        output_file (str): Output file path.

    Returns:
        str: Path to the saved file.
    """
    import pandas as pd
    import geopandas as gpd
    from shapely.geometry import Point

    # Load data
    df = pd.read_json('data/paczkomaty.json')
    df = pd.json_normalize(df.to_dict(orient='records'))
    df['geometry'] = df.apply(lambda row: Point(row['location.longitude'], row['location.latitude']), axis=1)
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

    # Create map
    m = LockerVisualization.create_base_map()
    m = LockerVisualization.create_heatmap(gdf)

    # Save map
    return LockerVisualization.save_map(m, output_file)

def create_score_heatmap(metric: str = 'overall_score', 
                        output_file: str = 'paczkomaty_score_map.html') -> str:
    """
    Create a heatmap of parcel locker scores.

    Args:
        metric (str): Metric to visualize ('overall_score', 'density_score', 'proximity_score', etc.).
        output_file (str): Output file path.

    Returns:
        str: Path to the saved file.
    """
    from parcel_analysis import ScoreCalculator

    # Initialize calculator
    calculator = ScoreCalculator()

    # Define bounds (Warsaw area)
    bounds = {
        'lat_min': 52.15,
        'lat_max': 52.30,
        'lon_min': 20.90,
        'lon_max': 21.10
    }

    # Create map
    m = LockerVisualization.create_grid_heatmap(
        calculator, bounds, grid_size=30, metric=metric
    )

    # Save map
    return LockerVisualization.save_map(m, output_file)

def create_advanced_score_heatmap(output_file: str = 'paczkomaty_advanced_score_map.html') -> str:
    """
    Create a heatmap of advanced parcel locker scores.

    Args:
        output_file (str): Output file path.

    Returns:
        str: Path to the saved file.
    """
    from parcel_analysis import ScoreCalculator

    # Initialize calculator
    calculator = ScoreCalculator()

    # Define bounds (Warsaw area)
    bounds = {
        'lat_min': 52.15,
        'lat_max': 52.30,
        'lon_min': 20.90,
        'lon_max': 21.10
    }

    # Create map
    m = LockerVisualization.create_advanced_heatmap(
        calculator, bounds, grid_size=30
    )

    # Save map
    return LockerVisualization.save_map(m, output_file)

# Example usage
if __name__ == "__main__":
    print("Creating density heatmap...")
    density_map = create_density_heatmap()
    print(f"Density heatmap created at: {density_map}")

    print("Creating score heatmap...")
    score_map = create_score_heatmap()
    print(f"Score heatmap created at: {score_map}")

    print("Creating advanced score heatmap...")
    advanced_map = create_advanced_score_heatmap()
    print(f"Advanced score heatmap created at: {advanced_map}")
