"""
Filtering functionality for parcel locker analysis.

This module provides methods for filtering parcel lockers by various attributes
and functions.
"""

import geopandas as gpd
from typing import Any, List

class LockerFilters:
    """
    A class providing filtering methods for parcel lockers.
    
    This class contains methods to filter parcel lockers by various attributes
    such as functions, 24/7 availability, easy access, etc.
    """
    
    @staticmethod
    def filter_by_attribute(gdf: gpd.GeoDataFrame, attribute: str, value: Any) -> gpd.GeoDataFrame:
        """
        Filter parcel lockers by a specific attribute value.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame to filter.
            attribute (str): Attribute name to filter by.
            value (Any): Value to filter for.

        Returns:
            gpd.GeoDataFrame: Filtered GeoDataFrame.
        """
        if attribute not in gdf.columns:
            raise ValueError(f"Attribute '{attribute}' not found in the data")

        return gdf[gdf[attribute] == value].copy()

    @staticmethod
    def filter_by_function(gdf: gpd.GeoDataFrame, function_name: str) -> gpd.GeoDataFrame:
        """
        Filter parcel lockers by a specific function they support.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame to filter.
            function_name (str): Function name to filter by.

        Returns:
            gpd.GeoDataFrame: Filtered GeoDataFrame.
        """
        # Check if functions column exists
        if 'functions' not in gdf.columns:
            raise ValueError("Functions column not found in the data")

        # Filter lockers that have the specified function
        return gdf[gdf['functions'].apply(lambda x: function_name in x if isinstance(x, list) else False)].copy()

    @staticmethod
    def filter_24_7_lockers(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Filter parcel lockers that are available 24/7.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame to filter.

        Returns:
            gpd.GeoDataFrame: Filtered GeoDataFrame with 24/7 lockers.
        """
        # Try different possible column names for 24/7 availability
        if 'location_247' in gdf.columns:
            return gdf[gdf['location_247'] == True].copy()
        elif 'opening_hours' in gdf.columns:
            return gdf[gdf['opening_hours'] == '24/7'].copy()
        else:
            raise ValueError("No column found to determine 24/7 availability")

    @staticmethod
    def filter_easy_access(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Filter parcel lockers with easy access.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame to filter.

        Returns:
            gpd.GeoDataFrame: Filtered GeoDataFrame with easy access lockers.
        """
        if 'easy_access_zone' not in gdf.columns:
            raise ValueError("Easy access zone column not found in the data")

        return gdf[gdf['easy_access_zone'] == True].copy()

    @staticmethod
    def search_by_address(gdf: gpd.GeoDataFrame, address_query: str) -> gpd.GeoDataFrame:
        """
        Search for parcel lockers by address.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame to search in.
            address_query (str): Address query string.

        Returns:
            gpd.GeoDataFrame: GeoDataFrame with matching lockers.
        """
        import pandas as pd
        
        # Convert query to lowercase for case-insensitive matching
        query_lower = address_query.lower()

        # Check for address columns
        address_columns = []
        for col in ['address.line1', 'address.line2', 'address_details.city', 
                   'address_details.street', 'address_details.post_code']:
            if col in gdf.columns:
                address_columns.append(col)

        if not address_columns:
            raise ValueError("No address columns found in the data")

        # Create a mask for matching addresses
        mask = pd.Series(False, index=gdf.index)
        for col in address_columns:
            # Convert column to string and lowercase
            col_values = gdf[col].astype(str).str.lower()
            mask = mask | col_values.str.contains(query_lower, na=False, regex=False)

        return gdf[mask].copy()

    @staticmethod
    def find_lockers_with_features(gdf: gpd.GeoDataFrame, 
                                  features: List[str] = None, 
                                  require_24_7: bool = False,
                                  require_easy_access: bool = False,
                                  require_payment: bool = False) -> gpd.GeoDataFrame:
        """
        Find parcel lockers with specific features.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame to filter.
            features (List[str], optional): List of required functions.
            require_24_7 (bool): Whether to require 24/7 availability.
            require_easy_access (bool): Whether to require easy access.
            require_payment (bool): Whether to require payment availability.

        Returns:
            gpd.GeoDataFrame: Filtered GeoDataFrame.
        """
        result = gdf.copy()
        
        # Apply filters based on parameters
        if features:
            for feature in features:
                result = LockerFilters.filter_by_function(result, feature)

        if require_24_7:
            result = LockerFilters.filter_24_7_lockers(result)

        if require_easy_access:
            result = LockerFilters.filter_easy_access(result)

        if require_payment and 'payment_available' in result.columns:
            result = result[result['payment_available'] == True].copy()

        return result