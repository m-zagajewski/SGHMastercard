"""
Parcel Analysis Package

This package provides tools for analyzing parcel locker locations,
calculating scores, optimizing placement, and visualizing results.
"""

# Import main components to expose at package level
from .core import ScoreCalculator
from .reporting import create_demo_report
from .visualization import (
    LockerVisualization,
    create_density_heatmap,
    create_score_heatmap,
    create_advanced_score_heatmap
)

# Version
__version__ = '1.0.0'
