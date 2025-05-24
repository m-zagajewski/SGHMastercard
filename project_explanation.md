# Parcel Locker Analysis Project

## Project Overview

This project is a comprehensive Python-based tool for analyzing parcel locker (paczkomaty) locations in Poland. It provides functionality for evaluating existing parcel locker placements, optimizing new locations, and visualizing the results through interactive maps and detailed reports.

## Core Functionality

The project offers several key capabilities:

1. **Location Scoring**: Evaluates locations based on multiple factors:
   - Density of parcel lockers in the area
   - Proximity to nearest parcel lockers
   - Accessibility features (24/7 availability, easy access)
   - Functionality (supported services)

2. **Advanced Analysis**: Performs comprehensive analysis of areas:
   - Statistics on locker types and distribution
   - Availability analysis (24/7, easy access, payment options)
   - Function analysis (supported services)

3. **Filtering**: Allows filtering parcel lockers by various attributes:
   - Specific functions (parcel collection, sending, etc.)
   - 24/7 availability
   - Easy access features
   - Address search

4. **Location Comparison**: Compares multiple locations to identify the best one based on customizable criteria.

5. **Optimization**: Finds optimal locations for new parcel lockers:
   - Grid-based search within a specified area
   - Recommendations for new locations based on existing coverage
   - Minimum distance constraints to avoid clustering

6. **Visualization**: Creates interactive maps to visualize:
   - Parcel locker density
   - Score distribution (overall, density, proximity, etc.)
   - Advanced score combining multiple metrics
   - Custom visualizations with markers and heatmaps

7. **Reporting**: Generates comprehensive reports summarizing the analysis results.

## Project Structure

The project is organized into a modular package structure:

- **Core Module**: Provides the fundamental ScoreCalculator class for loading data and calculating basic scores.
- **Analysis Module**: Extends the core functionality with advanced analysis capabilities.
- **Filters Module**: Provides methods for filtering parcel lockers by various attributes.
- **Optimization Module**: Implements algorithms for finding optimal locations.
- **Visualization Module**: Creates interactive maps and visualizations.
- **Reporting Module**: Generates comprehensive reports.

## Data

The project works with a dataset of parcel lockers in Poland, stored in JSON format. Each entry contains:
- Location information (latitude, longitude)
- Address details
- Type of location (indoor/outdoor)
- Opening hours
- Available functions
- Accessibility features
- Payment options

## Practical Applications

This tool can be used for:

1. **Business Decision Making**: Identifying optimal locations for new parcel lockers based on existing coverage.
2. **Network Optimization**: Analyzing the current distribution of parcel lockers to identify gaps and opportunities.
3. **Service Improvement**: Evaluating accessibility and functionality to enhance customer experience.
4. **Strategic Planning**: Comparing different locations to make data-driven decisions about expansion.
5. **Visual Analysis**: Creating interactive visualizations to better understand spatial patterns and trends.

## Technologies Used

The project leverages several key technologies:
- **GeoPandas**: For spatial data handling
- **Scikit-learn**: For spatial analysis (KDTree for nearest neighbor searches)
- **Folium**: For interactive map visualizations
- **Pandas**: For data manipulation
- **NumPy**: For numerical operations
- **Shapely**: For geometric operations

This project demonstrates a sophisticated approach to location-based analysis and optimization, providing valuable insights for parcel locker network planning and management.