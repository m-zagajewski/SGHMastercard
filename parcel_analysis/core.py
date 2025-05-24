"""
Core functionality for parcel locker analysis.

This module provides the core ScoreCalculator class with basic functionality
for loading data and calculating scores.
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from sklearn.neighbors import KDTree
from shapely.geometry import Point
import math
from typing import List, Dict, Any, Tuple, Optional, Union

class ScoreCalculator:
    """
    A class for calculating location-based scores using parcel locker data.

    This class provides functionality to evaluate a location based on its coordinates
    and a specified radius, considering factors such as density of parcel lockers
    and distance to the nearest ones.
    """

    def __init__(self, data_path='data/paczkomaty_processed.pkl', raw_data_path=None):
        """
        Initialize the ScoreCalculator with parcel locker data.

        Args:
            data_path (str): Path to the processed parcel locker data file.
            raw_data_path (str, optional): Path to the raw JSON data file. If provided,
                                          will process this file instead of using the pickle file.
        """
        if raw_data_path:
            self.gdf = self._process_raw_data(raw_data_path)
        else:
            self.gdf = self._load_data(data_path)

        # Ensure the geometry column exists and is valid
        if 'geometry' not in self.gdf.columns or not all(hasattr(g, 'x') and hasattr(g, 'y') for g in self.gdf.geometry):
            raise ValueError("Invalid geometry column in the data")

        self.coords = np.array(list(zip(self.gdf.geometry.x, self.gdf.geometry.y)))
        self.tree = KDTree(self.coords, leaf_size=2)

    def _process_raw_data(self, raw_data_path):
        """
        Process raw JSON data into a GeoDataFrame.

        Args:
            raw_data_path (str): Path to the raw JSON data file.

        Returns:
            gpd.GeoDataFrame: Processed geodataframe.
        """
        try:
            # Load JSON data
            df = pd.read_json(raw_data_path)

            # Normalize nested structures
            df = pd.json_normalize(df.to_dict(orient='records'))

            # Create geometry column
            df['geometry'] = df.apply(
                lambda row: Point(row['location.longitude'], row['location.latitude']) 
                if 'location.longitude' in row and 'location.latitude' in row 
                else None, 
                axis=1
            )

            # Remove rows with invalid geometry
            df = df.dropna(subset=['geometry'])

            # Convert to GeoDataFrame
            gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

            # Add density feature
            gdf = self._add_density_feature(gdf)

            return gdf

        except Exception as e:
            raise ValueError(f"Error processing raw data: {str(e)}")

    def _add_density_feature(self, gdf, radius=0.01):
        """
        Add density feature to the GeoDataFrame.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame to process.
            radius (float): Radius in degrees for density calculation.

        Returns:
            gpd.GeoDataFrame: GeoDataFrame with density feature added.
        """
        coords = np.array(list(zip(gdf.geometry.x, gdf.geometry.y)))
        tree = KDTree(coords, leaf_size=2)
        counts = tree.query_radius(coords, r=radius, count_only=True)
        gdf['density_1km'] = counts
        return gdf

    def _load_data(self, data_path):
        """
        Load the processed parcel locker data.

        Args:
            data_path (str): Path to the data file.

        Returns:
            gpd.GeoDataFrame: The loaded geodataframe.
        """
        try:
            gdf = pd.read_pickle(data_path)

            # Ensure it's a GeoDataFrame
            if not isinstance(gdf, gpd.GeoDataFrame):
                if 'geometry' in gdf.columns:
                    gdf = gpd.GeoDataFrame(gdf, geometry='geometry', crs="EPSG:4326")
                else:
                    raise ValueError("Loaded data is not a GeoDataFrame and has no geometry column")

            return gdf
        except FileNotFoundError:
            raise FileNotFoundError(f"Data file not found at {data_path}")
        except Exception as e:
            raise ValueError(f"Error loading data: {str(e)}")

    def _count_points_in_radius(self, lon, lat, radius):
        """
        Count the number of parcel lockers within the specified radius.

        Args:
            lon (float): Longitude of the point.
            lat (float): Latitude of the point.
            radius (float): Radius in degrees.

        Returns:
            int: Number of points within the radius.
        """
        point = np.array([[lon, lat]])
        indices = self.tree.query_radius(point, r=radius, return_distance=False)[0]
        return len(indices)

    def _get_nearest_points(self, lon, lat, k=5):
        """
        Find the k nearest parcel lockers to the specified point.

        Args:
            lon (float): Longitude of the point.
            lat (float): Latitude of the point.
            k (int): Number of nearest points to find.

        Returns:
            tuple: (distances, indices) of the nearest points.
        """
        point = np.array([[lon, lat]])
        distances, indices = self.tree.query(point, k=k)
        return distances[0], indices[0]

    def _calculate_density_score(self, count, max_count=20):
        """
        Calculate a score based on the density of parcel lockers.

        Args:
            count (int): Number of parcel lockers in the area.
            max_count (int): Maximum expected count for normalization.

        Returns:
            float: Density score between 0 and 1.
        """
        # Normalize count and apply a sigmoid-like function for smoother scaling
        normalized = min(count / max_count, 1.0)
        return 1 / (1 + math.exp(-10 * (normalized - 0.5)))

    def _calculate_proximity_score(self, distances):
        """
        Calculate a score based on the proximity to parcel lockers.

        Args:
            distances (np.array): Array of distances to nearest parcel lockers.

        Returns:
            float: Proximity score between 0 and 1.
        """
        if len(distances) == 0:
            return 0.0

        # Calculate weighted average of inverse distances
        weights = np.array([1.0, 0.8, 0.6, 0.4, 0.2])[:len(distances)]
        inv_distances = 1.0 / (1.0 + distances)  # Add 1 to avoid division by zero

        return np.sum(weights * inv_distances) / np.sum(weights)

    def get_points_in_radius(self, lat: float, lon: float, radius: float) -> gpd.GeoDataFrame:
        """
        Get all parcel lockers within the specified radius.

        Args:
            lat (float): Latitude of the point.
            lon (float): Longitude of the point.
            radius (float): Radius in degrees.

        Returns:
            gpd.GeoDataFrame: GeoDataFrame containing parcel lockers within the radius.
        """
        point = np.array([[lon, lat]])
        indices = self.tree.query_radius(point, r=radius, return_distance=False)[0]
        return self.gdf.iloc[indices].copy()

    def calculate_score(self, lat, lon, radius):
        """
        Calculate a basic score for a location based on density and proximity.

        Args:
            lat (float): Latitude of the point.
            lon (float): Longitude of the point.
            radius (float): Radius in degrees to consider.

        Returns:
            dict: Dictionary containing the score components.
        """
        # Get points in radius
        points_in_radius = self.get_points_in_radius(lat, lon, radius)
        count = len(points_in_radius)

        # Get nearest points
        distances, indices = self._get_nearest_points(lon, lat)

        # Calculate component scores
        density_score = self._calculate_density_score(count)
        proximity_score = self._calculate_proximity_score(distances)

        # Calculate overall score (weighted average)
        overall_score = 0.6 * density_score + 0.4 * proximity_score

        return {
            'overall_score': overall_score,
            'density_score': density_score,
            'proximity_score': proximity_score,
            'points_in_radius': count,
            'nearest_distances': distances.tolist()
        }