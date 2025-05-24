# Parcel Locker Heatmap Visualization

This document provides an overview of the heatmap visualization functionality added to the parcel analysis package.

## Overview

The heatmap visualization functionality allows you to create interactive heatmaps to visualize various metrics related to parcel locker locations, such as:

- Density of parcel lockers
- Overall score
- Density score
- Proximity score
- Advanced score (combining density, proximity, accessibility, and functionality)

These visualizations can help identify optimal locations for new parcel lockers, analyze the coverage of existing lockers, and understand the distribution of different metrics across geographic areas.

## Features

The visualization module provides the following features:

1. **Basic Density Heatmap**: Visualize the density of parcel lockers across a geographic area.
2. **Score Heatmap**: Visualize different score metrics (overall, density, proximity) across a geographic area.
3. **Advanced Score Heatmap**: Visualize advanced scores that combine multiple metrics.
4. **Custom Heatmaps**: Create heatmaps with custom bounds, grid sizes, and metrics.
5. **Combined Visualizations**: Create maps that combine markers and heatmaps for a more comprehensive view.

## Usage

### Basic Usage

```python
from parcel_analysis import create_density_heatmap, create_score_heatmap, create_advanced_score_heatmap

# Create a density heatmap
density_map_path = create_density_heatmap()
print(f"Density heatmap created at: {density_map_path}")

# Create a score heatmap
score_map_path = create_score_heatmap(metric='overall_score')
print(f"Score heatmap created at: {score_map_path}")

# Create an advanced score heatmap
advanced_map_path = create_advanced_score_heatmap()
print(f"Advanced score heatmap created at: {advanced_map_path}")
```

### Advanced Usage

For more advanced usage, you can use the `LockerVisualization` class directly:

```python
from parcel_analysis import ScoreCalculator, LockerVisualization
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium

# Load data
df = pd.read_json('data/paczkomaty.json')
df = pd.json_normalize(df.to_dict(orient='records'))
df['geometry'] = df.apply(lambda row: Point(row['location.longitude'], row['location.latitude']), axis=1)
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

# Create a base map
m = LockerVisualization.create_base_map(center=[52.2297, 21.0122], zoom_start=12)

# Add markers
m = LockerVisualization.create_marker_map(gdf=gdf, popup_col='name', map_obj=m, cluster=True)

# Add a heatmap layer
m = LockerVisualization.create_heatmap(
    gdf=gdf,
    value_col='density_1km' if 'density_1km' in gdf.columns else None,
    map_obj=m,
    radius=15,
    blur=10
)

# Add layer control
folium.LayerControl().add_to(m)

# Save the map
map_path = LockerVisualization.save_map(m, 'custom_map.html')
print(f"Custom map created at: {map_path}")
```

### Creating Grid-Based Heatmaps

You can also create grid-based heatmaps that calculate scores for a grid of points:

```python
from parcel_analysis import ScoreCalculator, LockerVisualization

# Initialize calculator
calculator = ScoreCalculator()

# Define bounds
bounds = {
    'lat_min': 52.15,
    'lat_max': 52.30,
    'lon_min': 20.90,
    'lon_max': 21.10
}

# Create a grid-based heatmap
m = LockerVisualization.create_grid_heatmap(
    calculator=calculator,
    bounds=bounds,
    grid_size=30,
    metric='overall_score'
)

# Save the map
map_path = LockerVisualization.save_map(m, 'grid_heatmap.html')
print(f"Grid heatmap created at: {map_path}")
```

## Examples

For more examples, see the `heatmap_example.py` script, which demonstrates various ways to use the heatmap visualization functionality.

## Output

The heatmap visualizations are saved as HTML files that can be opened in any web browser. The HTML files include interactive maps that allow you to:

- Zoom in and out
- Pan around
- Toggle layers (if multiple layers are present)
- View tooltips and popups (if markers are present)

## Dependencies

The heatmap visualization functionality depends on the following libraries:

- folium
- folium.plugins (HeatMap, MarkerCluster)
- geopandas
- pandas
- numpy
- branca.colormap

These dependencies are automatically imported when you import the visualization module.