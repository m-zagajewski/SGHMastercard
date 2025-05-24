"""
Optimization functionality for parcel locker analysis.

This module provides methods for optimizing parcel locker locations,
including finding optimal locations and recommending new locations.
"""

import numpy as np
from typing import Dict, Any, List, Tuple

class LocationOptimizer:
    """
    A class providing optimization methods for parcel locker locations.
    
    This class contains methods to find optimal locations and recommend
    new locations for parcel lockers.
    """
    
    @staticmethod
    def find_optimal_location(lat_min: float, lat_max: float, lon_min: float, lon_max: float, 
                             grid_size: int = 5, radius: float = 0.01,
                             score_calculator=None) -> Dict[str, Any]:
        """
        Find the optimal location within a bounding box by evaluating a grid of points.

        Args:
            lat_min (float): Minimum latitude of the bounding box.
            lat_max (float): Maximum latitude of the bounding box.
            lon_min (float): Minimum longitude of the bounding box.
            lon_max (float): Maximum longitude of the bounding box.
            grid_size (int): Number of points to evaluate in each dimension.
            radius (float): Radius in degrees to consider for each point.
            score_calculator: An instance of ScoreCalculator to calculate scores.

        Returns:
            Dict[str, Any]: Optimal location and its score.
        """
        if not score_calculator:
            raise ValueError("A ScoreCalculator instance is required")
            
        lat_step = (lat_max - lat_min) / (grid_size - 1) if grid_size > 1 else 0
        lon_step = (lon_max - lon_min) / (grid_size - 1) if grid_size > 1 else 0

        best_score = -1
        best_location = None
        all_scores = []

        for i in range(grid_size):
            for j in range(grid_size):
                lat = lat_min + i * lat_step
                lon = lon_min + j * lon_step

                score_result = score_calculator.calculate_score(lat, lon, radius)
                score = score_result['overall_score']

                all_scores.append({
                    "coordinates": (lat, lon),
                    "score": score,
                    "details": score_result
                })

                if score > best_score:
                    best_score = score
                    best_location = (lat, lon)

        return {
            "optimal_location": best_location,
            "optimal_score": best_score,
            "all_evaluated_locations": all_scores
        }

    @staticmethod
    def recommend_new_locations(existing_locations: List[Dict[str, float]], 
                               search_area: Dict[str, float],
                               score_calculator=None,
                               num_recommendations: int = 3,
                               min_distance: float = 0.02) -> List[Dict[str, Any]]:
        """
        Recommend locations for new parcel lockers based on existing coverage.

        Args:
            existing_locations (List[Dict[str, float]]): List of existing locations with 'lat' and 'lon'.
            search_area (Dict[str, float]): Bounding box with 'lat_min', 'lat_max', 'lon_min', 'lon_max'.
            score_calculator: An instance of ScoreCalculator to calculate scores.
            num_recommendations (int): Number of recommendations to provide.
            min_distance (float): Minimum distance between recommendations in degrees.

        Returns:
            List[Dict[str, Any]]: List of recommended locations with scores.
        """
        if not score_calculator:
            raise ValueError("A ScoreCalculator instance is required")
            
        # Validate inputs
        required_keys = ['lat_min', 'lat_max', 'lon_min', 'lon_max']
        if not all(k in search_area for k in required_keys):
            raise ValueError(f"search_area must contain keys: {required_keys}")

        # Create a grid of potential locations
        grid_size = max(10, int(num_recommendations * 3))  # Ensure enough candidates

        # Find optimal location
        optimal = LocationOptimizer.find_optimal_location(
            search_area['lat_min'], search_area['lat_max'],
            search_area['lon_min'], search_area['lon_max'],
            grid_size=grid_size,
            radius=min_distance,
            score_calculator=score_calculator
        )

        # Sort all evaluated locations by score
        candidates = sorted(
            optimal['all_evaluated_locations'], 
            key=lambda x: x['score'], 
            reverse=True
        )

        # Filter candidates to ensure minimum distance between recommendations
        recommendations = []
        for candidate in candidates:
            # Skip if too close to existing locations
            too_close = False
            for existing in existing_locations:
                dist = np.sqrt((candidate['coordinates'][0] - existing['lat'])**2 + 
                              (candidate['coordinates'][1] - existing['lon'])**2)
                if dist < min_distance:
                    too_close = True
                    break

            # Skip if too close to already recommended locations
            for rec in recommendations:
                dist = np.sqrt((candidate['coordinates'][0] - rec['coordinates'][0])**2 + 
                              (candidate['coordinates'][1] - rec['coordinates'][1])**2)
                if dist < min_distance:
                    too_close = True
                    break

            if not too_close:
                recommendations.append({
                    'coordinates': candidate['coordinates'],
                    'score': candidate['score'],
                    'details': candidate['details']
                })

                if len(recommendations) >= num_recommendations:
                    break

        return recommendations