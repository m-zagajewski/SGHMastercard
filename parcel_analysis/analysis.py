"""
Analysis functionality for parcel locker analysis.

This module provides methods for analyzing parcel locker data, including
calculating various scores and performing comprehensive area analysis.
"""

import geopandas as gpd
import pandas as pd
from typing import Dict, Any, List

class LockerAnalysis:
    """
    A class providing analysis methods for parcel lockers.

    This class contains methods to analyze parcel lockers, calculate various
    scores, and perform comprehensive area analysis.
    """

    @staticmethod
    def calculate_accessibility_score(gdf: gpd.GeoDataFrame) -> float:
        """
        Calculate an accessibility score based on 24/7 availability and easy access.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame to analyze.

        Returns:
            float: Accessibility score between 0 and 1.
        """
        if len(gdf) == 0:
            return 0.0

        score = 0.0
        count = 0

        # Check 24/7 availability
        if 'location_247' in gdf.columns:
            score += gdf['location_247'].mean()
            count += 1
        elif 'opening_hours' in gdf.columns:
            score += (gdf['opening_hours'] == '24/7').mean()
            count += 1

        # Check easy access
        if 'easy_access_zone' in gdf.columns:
            score += gdf['easy_access_zone'].mean()
            count += 1

        # Check payment availability
        if 'payment_available' in gdf.columns:
            score += gdf['payment_available'].mean()
            count += 1

        return score / max(1, count)

    @staticmethod
    def calculate_functionality_score(gdf: gpd.GeoDataFrame) -> float:
        """
        Calculate a score based on the number of functions supported by parcel lockers.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame to analyze.

        Returns:
            float: Functionality score between 0 and 1.
        """
        if len(gdf) == 0 or 'functions' not in gdf.columns:
            return 0.0

        # Calculate average number of functions
        function_counts = gdf['functions'].apply(lambda x: len(x) if isinstance(x, list) else 0)
        avg_functions = function_counts.mean()

        # Normalize by expected maximum (from data inspection)
        max_functions = 15  # Adjust based on actual data
        return min(avg_functions / max_functions, 1.0)

    @staticmethod
    def analyze_area(gdf: gpd.GeoDataFrame, score_result: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform a comprehensive analysis of an area.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame containing parcel lockers in the area.
            score_result (Dict[str, Any], optional): Score result from ScoreCalculator.

        Returns:
            Dict[str, Any]: Dictionary with analysis results.
        """
        if len(gdf) == 0:
            return {"error": "No parcel lockers found in the specified area"}

        # Basic statistics
        stats = {
            "total_lockers": len(gdf),
        }

        if score_result:
            stats["score"] = score_result

        # Location type distribution
        if 'location_type' in gdf.columns:
            location_types = gdf['location_type'].value_counts().to_dict()
            stats["location_type_distribution"] = location_types

        # 24/7 availability
        if 'location_247' in gdf.columns:
            stats["24_7_available"] = gdf['location_247'].sum()
            stats["24_7_percentage"] = (gdf['location_247'].sum() / len(gdf)) * 100
        elif 'opening_hours' in gdf.columns:
            twenty_four_seven = (gdf['opening_hours'] == '24/7').sum()
            stats["24_7_available"] = twenty_four_seven
            stats["24_7_percentage"] = (twenty_four_seven / len(gdf)) * 100

        # Easy access
        if 'easy_access_zone' in gdf.columns:
            stats["easy_access_available"] = gdf['easy_access_zone'].sum()
            stats["easy_access_percentage"] = (gdf['easy_access_zone'].sum() / len(gdf)) * 100

        # Payment availability
        if 'payment_available' in gdf.columns:
            stats["payment_available"] = gdf['payment_available'].sum()
            stats["payment_percentage"] = (gdf['payment_available'].sum() / len(gdf)) * 100

        # Function analysis
        if 'functions' in gdf.columns:
            all_functions = []
            for funcs in gdf['functions']:
                if isinstance(funcs, list):
                    all_functions.extend(funcs)

            function_counts = pd.Series(all_functions).value_counts().to_dict()
            stats["function_distribution"] = function_counts
            stats["avg_functions_per_locker"] = len(all_functions) / len(gdf)

        return stats

    @staticmethod
    def compare_locations(locations_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple locations based on their scores.

        Args:
            locations_data (List[Dict[str, Any]]): List of location data with scores and analysis.

        Returns:
            Dict[str, Any]: Comparison results.
        """
        if not locations_data:
            return {"error": "No locations provided for comparison"}

        # Sort by overall score
        # Handle both nested dictionary and direct score value
        def get_score(location):
            score = location.get("score")
            if isinstance(score, dict):
                return score.get("overall_score", 0)
            elif isinstance(score, (int, float)):
                return score
            return 0

        sorted_locations = sorted(
            locations_data, 
            key=get_score, 
            reverse=True
        )

        return {
            "best_location_index": sorted_locations[0].get("location_index") if sorted_locations else None,
            "location_rankings": sorted_locations
        }

    @staticmethod
    def calculate_advanced_score(basic_score: Dict[str, Any], 
                                accessibility_score: float, 
                                functionality_score: float) -> Dict[str, Any]:
        """
        Calculate an advanced score incorporating accessibility and functionality.

        Args:
            basic_score (Dict[str, Any]): Basic score from ScoreCalculator.
            accessibility_score (float): Accessibility score.
            functionality_score (float): Functionality score.

        Returns:
            Dict[str, Any]: Advanced score with all components.
        """
        # Define weights for each component
        weights = {
            'density': 0.3,
            'proximity': 0.3,
            'accessibility': 0.2,
            'functionality': 0.2
        }

        # Calculate overall score (weighted average of all components)
        overall_score = (
            weights['density'] * basic_score.get('density_score', 0) +
            weights['proximity'] * basic_score.get('proximity_score', 0) +
            weights['accessibility'] * accessibility_score +
            weights['functionality'] * functionality_score
        )

        # Create a new score dictionary with all components
        advanced_score = basic_score.copy()
        advanced_score['overall_score'] = overall_score
        advanced_score['accessibility_score'] = accessibility_score
        advanced_score['functionality_score'] = functionality_score

        return advanced_score
