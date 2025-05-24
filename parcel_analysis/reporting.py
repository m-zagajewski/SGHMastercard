"""
Reporting functionality for parcel locker analysis.

This module provides functions for generating reports based on parcel locker
analysis results.
"""

from typing import Dict, Any, List, Optional
import os

def create_demo_report(calculator=None, output_file='parcel_locker_analysis_report.txt'):
    """
    Create a comprehensive demonstration report of the parcel analysis capabilities.

    Args:
        calculator: An instance of ScoreCalculator to use for analysis.
        output_file (str): Path to save the report.
        
    Returns:
        str: Path to the created report file.
    """
    if calculator is None:
        from .core import ScoreCalculator
        calculator = ScoreCalculator()
        
    from .filters import LockerFilters
    from .analysis import LockerAnalysis
    from .optimization import LocationOptimizer

    with open(output_file, 'w') as f:
        # Header
        f.write("=" * 80 + "\n")
        f.write("PARCEL LOCKER LOCATION ANALYSIS REPORT\n")
        f.write("=" * 80 + "\n\n")

        # Basic Score Calculation
        f.write("1. BASIC SCORE CALCULATION\n")
        f.write("-" * 40 + "\n")

        # Example coordinates (Warsaw city center)
        lat = 52.2297
        lon = 21.0122
        radius = 0.01  # approximately 1km in degrees

        result = calculator.calculate_score(lat, lon, radius)

        f.write(f"Location: Warsaw City Center ({lat}, {lon}), Radius: {radius} degrees\n\n")
        f.write(f"Overall Score: {result.get('overall_score', 'N/A'):.2f}\n")
        f.write(f"Density Score: {result.get('density_score', 'N/A'):.2f}\n")
        f.write(f"Proximity Score: {result.get('proximity_score', 'N/A'):.2f}\n")
        
        if 'accessibility_score' in result:
            f.write(f"Accessibility Score: {result['accessibility_score']:.2f}\n")
        if 'functionality_score' in result:
            f.write(f"Functionality Score: {result['functionality_score']:.2f}\n")
            
        f.write(f"Number of parcel lockers within radius: {result.get('points_in_radius', 'N/A')}\n")
        
        if 'nearest_distances' in result:
            f.write(f"Distances to 5 nearest parcel lockers: {[f'{d:.4f}' for d in result['nearest_distances']]}\n\n")

        # Advanced Area Analysis
        f.write("2. ADVANCED AREA ANALYSIS\n")
        f.write("-" * 40 + "\n")

        try:
            # Get points in radius
            points_in_radius = calculator.get_points_in_radius(lat, lon, radius)
            
            # Calculate advanced scores
            accessibility_score = LockerAnalysis.calculate_accessibility_score(points_in_radius)
            functionality_score = LockerAnalysis.calculate_functionality_score(points_in_radius)
            
            # Create advanced score
            advanced_score = LockerAnalysis.calculate_advanced_score(
                result, accessibility_score, functionality_score
            )
            
            # Analyze area
            analysis = LockerAnalysis.analyze_area(points_in_radius, advanced_score)

            f.write(f"Total lockers in area: {analysis.get('total_lockers', 'N/A')}\n")

            if "location_type_distribution" in analysis:
                f.write("Location Type Distribution:\n")
                for loc_type, count in analysis["location_type_distribution"].items():
                    f.write(f"  - {loc_type}: {count}\n")

            f.write(f"24/7 availability: {analysis.get('24_7_percentage', 'N/A'):.1f}%\n")
            f.write(f"Easy access availability: {analysis.get('easy_access_percentage', 'N/A'):.1f}%\n")
            f.write(f"Payment availability: {analysis.get('payment_percentage', 'N/A'):.1f}%\n")

            if "function_distribution" in analysis:
                f.write("\nTop 5 Functions:\n")
                top_functions = sorted(
                    analysis["function_distribution"].items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:5]
                for func, count in top_functions:
                    f.write(f"  - {func}: {count}\n")

            f.write(f"Average functions per locker: {analysis.get('avg_functions_per_locker', 'N/A'):.1f}\n\n")
        except Exception as e:
            f.write(f"Error in advanced area analysis: {str(e)}\n\n")

        # Feature-based Filtering
        f.write("3. FEATURE-BASED FILTERING\n")
        f.write("-" * 40 + "\n")

        # Find lockers with specific features
        try:
            points_in_radius = calculator.get_points_in_radius(lat, lon, radius)
            feature_lockers = LockerFilters.find_lockers_with_features(
                points_in_radius,
                features=["parcel_collect", "parcel_send"],
                require_24_7=True,
                require_easy_access=True
            )

            f.write(f"Lockers with parcel_collect, parcel_send, 24/7 and easy access: {len(feature_lockers)}\n\n")
        except Exception as e:
            f.write(f"Error in feature filtering: {str(e)}\n\n")

        # Location Comparison
        f.write("4. LOCATION COMPARISON\n")
        f.write("-" * 40 + "\n")

        locations = [
            {"lat": 52.2297, "lon": 21.0122, "name": "Warsaw Center"},
            {"lat": 52.1793, "lon": 20.9984, "name": "Warsaw South"},
            {"lat": 52.2600, "lon": 21.0300, "name": "Warsaw North"}
        ]

        try:
            # Prepare location data for comparison
            locations_data = []
            for i, loc in enumerate(locations):
                # Calculate score
                score = calculator.calculate_score(loc['lat'], loc['lon'], radius)
                
                # Get points in radius
                points = calculator.get_points_in_radius(loc['lat'], loc['lon'], radius)
                
                # Calculate advanced scores
                accessibility = LockerAnalysis.calculate_accessibility_score(points)
                functionality = LockerAnalysis.calculate_functionality_score(points)
                
                # Create advanced score
                advanced_score = LockerAnalysis.calculate_advanced_score(
                    score, accessibility, functionality
                )
                
                # Analyze area
                analysis = LockerAnalysis.analyze_area(points, advanced_score)
                
                # Add to locations data
                locations_data.append({
                    "location_index": i,
                    "name": loc.get("name", f"Location {i}"),
                    "coordinates": (loc['lat'], loc['lon']),
                    "score": advanced_score['overall_score'],
                    "total_lockers": analysis.get("total_lockers", 0),
                    "24_7_percentage": analysis.get("24_7_percentage", 0),
                    "easy_access_percentage": analysis.get("easy_access_percentage", 0)
                })
            
            # Compare locations
            comparison = LockerAnalysis.compare_locations(locations_data)

            f.write(f"Best location: {locations[comparison['best_location_index']]['name']}\n\n")
            f.write("Rankings:\n")
            for loc in comparison['location_rankings']:
                f.write(f"  {loc['name']}: Score {loc['score']:.2f}, Lockers: {loc['total_lockers']}\n")
                f.write(f"    24/7 availability: {loc.get('24_7_percentage', 0):.1f}%\n")
                f.write(f"    Easy access: {loc.get('easy_access_percentage', 0):.1f}%\n\n")
        except Exception as e:
            f.write(f"Error in location comparison: {str(e)}\n\n")

        # Optimal Location Finding
        f.write("5. OPTIMAL LOCATION FINDING\n")
        f.write("-" * 40 + "\n")

        # Define a search area (small area around Warsaw)
        search_area = {
            "lat_min": 52.15,
            "lat_max": 52.30,
            "lon_min": 20.90,
            "lon_max": 21.10
        }

        try:
            optimal = LocationOptimizer.find_optimal_location(
                search_area['lat_min'], search_area['lat_max'],
                search_area['lon_min'], search_area['lon_max'],
                grid_size=3,  # Small grid for demonstration
                radius=radius,
                score_calculator=calculator
            )

            f.write(f"Optimal location: {optimal['optimal_location']}\n")
            f.write(f"Optimal score: {optimal['optimal_score']:.2f}\n\n")

            f.write("All evaluated locations:\n")
            for i, loc in enumerate(optimal['all_evaluated_locations'][:3]):  # Show top 3
                f.write(f"  {i+1}. Coordinates: {loc['coordinates']}, Score: {loc['score']:.2f}\n")
        except Exception as e:
            f.write(f"Error in optimal location finding: {str(e)}\n\n")

        # New Location Recommendations
        f.write("\n6. NEW LOCATION RECOMMENDATIONS\n")
        f.write("-" * 40 + "\n")

        # Use existing locations from the data
        existing = [
            {"lat": 52.2297, "lon": 21.0122},
            {"lat": 52.1793, "lon": 20.9984},
            {"lat": 52.2600, "lon": 21.0300}
        ]

        try:
            recommendations = LocationOptimizer.recommend_new_locations(
                existing,
                search_area,
                score_calculator=calculator,
                num_recommendations=2,
                min_distance=0.02
            )

            f.write(f"Number of recommendations: {len(recommendations)}\n\n")

            for i, rec in enumerate(recommendations):
                f.write(f"Recommendation {i+1}:\n")
                f.write(f"  Coordinates: {rec['coordinates']}\n")
                f.write(f"  Score: {rec['score']:.2f}\n")
                f.write(f"  Density Score: {rec['details']['density_score']:.2f}\n")
                f.write(f"  Proximity Score: {rec['details']['proximity_score']:.2f}\n\n")
        except Exception as e:
            f.write(f"Error in location recommendations: {str(e)}\n\n")

        # Conclusion
        f.write("=" * 80 + "\n")
        f.write("CONCLUSION\n")
        f.write("=" * 80 + "\n\n")
        f.write("This report demonstrates the powerful features of the parcel analysis package for\n")
        f.write("analyzing parcel locker locations. The package provides comprehensive tools for\n")
        f.write("location scoring, area analysis, feature-based filtering, location comparison,\n")
        f.write("optimal location finding, and new location recommendations.\n\n")
        f.write("These capabilities can be used to make data-driven decisions about parcel locker\n")
        f.write("placement, optimize delivery networks, and improve customer service.\n")

    print(f"Demonstration report created at {output_file}")
    return output_file