"""
Backward compatibility module for the parcel_analysis package.

This module imports and re-exports the functionality from the parcel_analysis
package to maintain backward compatibility with existing code.
"""

from parcel_analysis import ScoreCalculator, create_demo_report

# Example usage
if __name__ == "__main__":
    from parcel_analysis.filters import LockerFilters
    from parcel_analysis.analysis import LockerAnalysis
    from parcel_analysis.optimization import LocationOptimizer

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

    if 'accessibility_score' in result:
        print(f"Accessibility Score: {result['accessibility_score']:.2f}")
    if 'functionality_score' in result:
        print(f"Functionality Score: {result['functionality_score']:.2f}")

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

    # Analyze area
    analysis = LockerAnalysis.analyze_area(points_in_radius, advanced_score)
    print(f"Total lockers in area: {analysis.get('total_lockers', 'N/A')}")
    print(f"24/7 availability: {analysis.get('24_7_percentage', 'N/A'):.1f}%")
    print(f"Easy access availability: {analysis.get('easy_access_percentage', 'N/A'):.1f}%")

    print("\n=== Location Comparison ===")
    # Compare multiple locations
    locations = [
        {"lat": 52.2297, "lon": 21.0122},  # Warsaw center
        {"lat": 52.1793, "lon": 20.9984},  # Warsaw south
        {"lat": 52.2600, "lon": 21.0300}   # Warsaw north
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
            "coordinates": (loc['lat'], loc['lon']),
            "score": advanced_score['overall_score'],
            "total_lockers": analysis.get("total_lockers", 0),
            "24_7_percentage": analysis.get("24_7_percentage", 0),
            "easy_access_percentage": analysis.get("easy_access_percentage", 0)
        })

    # Compare locations
    comparison = LockerAnalysis.compare_locations(locations_data)
    print(f"Best location index: {comparison['best_location_index']}")
    print("Rankings:")
    for loc in comparison['location_rankings']:
        print(f"  Location {loc['location_index']}: Score {loc['score']:.2f}, Lockers: {loc['total_lockers']}")

    # Generate a comprehensive demonstration report
    print("\n=== Generating Comprehensive Report ===")
    report_file = create_demo_report(calculator)
