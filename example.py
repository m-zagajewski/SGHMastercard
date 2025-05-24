"""
Example usage of the parcel_analysis package.

This script demonstrates how to use the parcel_analysis package to analyze
parcel locker locations.
"""

from parcel_analysis import (
    ScoreCalculator, 
    create_demo_report,
    LockerVisualization,
    create_density_heatmap,
    create_score_heatmap,
    create_advanced_score_heatmap
)
from parcel_analysis.filters import LockerFilters
from parcel_analysis.analysis import LockerAnalysis
from parcel_analysis.optimization import LocationOptimizer

def main():
    # Initialize the ScoreCalculator
    calculator = ScoreCalculator()

    print("=== Basic Score Calculation ===")
    # Example coordinates (Warsaw city center)
    lat = 52.2297
    lon = 21.0122
    radius = 0.01  # approximately 1km in degrees

    # Calculate basic score
    result = calculator.calculate_score(lat, lon, radius)

    print(f"Location Score Analysis for coordinates ({lat}, {lon}) with radius {radius}:")
    print(f"Overall Score: {result['overall_score']:.2f}")
    print(f"Density Score: {result['density_score']:.2f}")
    print(f"Proximity Score: {result['proximity_score']:.2f}")
    print(f"Number of parcel lockers within radius: {result['points_in_radius']}")
    print(f"Distances to 5 nearest parcel lockers: {[f'{d:.4f}' for d in result['nearest_distances']]}")

    # Get points in radius for further analysis
    points_in_radius = calculator.get_points_in_radius(lat, lon, radius)

    print("\n=== Advanced Analysis ===")
    # Calculate advanced scores
    accessibility_score = LockerAnalysis.calculate_accessibility_score(points_in_radius)
    functionality_score = LockerAnalysis.calculate_functionality_score(points_in_radius)

    # Create advanced score
    advanced_score = LockerAnalysis.calculate_advanced_score(
        result, accessibility_score, functionality_score
    )

    print(f"Accessibility Score: {advanced_score['accessibility_score']:.2f}")
    print(f"Functionality Score: {advanced_score['functionality_score']:.2f}")
    print(f"Advanced Overall Score: {advanced_score['overall_score']:.2f}")

    # Analyze area
    analysis = LockerAnalysis.analyze_area(points_in_radius, advanced_score)
    print(f"Total lockers in area: {analysis.get('total_lockers', 'N/A')}")
    print(f"24/7 availability: {analysis.get('24_7_percentage', 'N/A'):.1f}%")
    print(f"Easy access availability: {analysis.get('easy_access_percentage', 'N/A'):.1f}%")

    print("\n=== Filtering ===")
    # Filter lockers with specific features
    try:
        feature_lockers = LockerFilters.find_lockers_with_features(
            points_in_radius,
            features=["parcel_collect", "parcel_send"],
            require_24_7=True
        )
        print(f"Lockers with parcel_collect, parcel_send, and 24/7 availability: {len(feature_lockers)}")
    except Exception as e:
        print(f"Error in feature filtering: {str(e)}")

    print("\n=== Location Comparison ===")
    # Compare multiple locations
    locations = [
        {"lat": 52.2297, "lon": 21.0122, "name": "Warsaw Center"},
        {"lat": 52.1793, "lon": 20.9984, "name": "Warsaw South"},
        {"lat": 52.2600, "lon": 21.0300, "name": "Warsaw North"}
    ]

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
    print(f"Best location: {locations[comparison['best_location_index']]['name']}")
    print("Rankings:")
    for loc in comparison['location_rankings']:
        print(f"  {loc['name']}: Score {loc['score']:.2f}, Lockers: {loc['total_lockers']}")

    print("\n=== Optimization ===")
    # Define a search area (small area around Warsaw)
    search_area = {
        "lat_min": 52.15,
        "lat_max": 52.30,
        "lon_min": 20.90,
        "lon_max": 21.10
    }

    # Find optimal location
    try:
        optimal = LocationOptimizer.find_optimal_location(
            search_area['lat_min'], search_area['lat_max'],
            search_area['lon_min'], search_area['lon_max'],
            grid_size=3,  # Small grid for demonstration
            radius=radius,
            score_calculator=calculator
        )

        print(f"Optimal location: {optimal['optimal_location']}")
        print(f"Optimal score: {optimal['optimal_score']:.2f}")
    except Exception as e:
        print(f"Error in optimal location finding: {str(e)}")

    # Generate a comprehensive demonstration report
    print("\n=== Generating Comprehensive Report ===")
    report_file = create_demo_report(calculator)
    print(f"Report created at: {report_file}")

    # Create visualizations
    print("\n=== Creating Visualizations ===")

    # Create a density heatmap
    print("Creating a density heatmap...")
    density_map_path = create_density_heatmap()
    print(f"Density heatmap created at: {density_map_path}")

    # Create a score heatmap
    print("\nCreating a score heatmap...")
    score_map_path = create_score_heatmap(metric='overall_score')
    print(f"Score heatmap created at: {score_map_path}")

    # Create an advanced score heatmap
    print("\nCreating an advanced score heatmap...")
    advanced_map_path = create_advanced_score_heatmap()
    print(f"Advanced score heatmap created at: {advanced_map_path}")

    print("\nAll visualizations have been created successfully!")
    print("Open the HTML files in a web browser to view the interactive maps.")

if __name__ == "__main__":
    main()
