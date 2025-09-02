"""
Data loader module for Daily Breakdown System.
Handles data loading, preprocessing, and validation.
"""

from typing import Tuple, Optional
import pandas as pd
import os


class DataLoader:
    """
    Data loading and preprocessing class.
    
    This class handles loading and cleaning of business plan data
    and date dimension data.
    """
    
    @staticmethod
    def load_business_plan(file_path: str) -> pd.DataFrame:
        """
        Load and clean business plan data.
        
        Args:
            file_path: Path to the business plan CSV file
        
        Returns:
            Cleaned business plan DataFrame
        
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is invalid
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Business plan file not found: {file_path}")
        
        try:
            bp = pd.read_csv(file_path)
            
            # Validate required columns
            required_columns = ['year', 'month', 'line', 'metric', 'sub_metric', 'target', 'unit']
            missing_columns = [col for col in required_columns if col not in bp.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Clean target column (remove commas and convert to float)
            if 'target' in bp.columns:
                bp['target'] = bp['target'].str.replace(',', '').astype(float)
            
            # Validate data types
            bp['year'] = bp['year'].astype(int)
            bp['month'] = bp['month'].astype(int)
            
            return bp
            
        except Exception as e:
            raise ValueError(f"Error loading business plan data: {str(e)}")
    
    @staticmethod
    def load_date_dimension(file_path: str) -> pd.DataFrame:
        """
        Load and clean date dimension data.
        
        Args:
            file_path: Path to the date dimension CSV file
        
        Returns:
            Cleaned date dimension DataFrame
        
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is invalid
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Date dimension file not found: {file_path}")
        
        try:
            dim_date = pd.read_csv(file_path)
            
            # Validate required columns
            required_columns = ['persian_year', 'persian_month_number', 'persian_date', 'date_id', 'date_string']
            missing_columns = [col for col in required_columns if col not in dim_date.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Rename columns for consistency
            dim_date.rename(columns={
                'persian_year': 'year',
                'persian_month_number': 'month',
                'persian_date': 'persian_date'
            }, inplace=True)
            
            # Validate data types
            dim_date['year'] = dim_date['year'].astype(int)
            dim_date['month'] = dim_date['month'].astype(int)
            dim_date['persian_date'] = dim_date['persian_date'].astype(str)
            
            return dim_date
            
        except Exception as e:
            raise ValueError(f"Error loading date dimension data: {str(e)}")
    
    @staticmethod
    def validate_data_compatibility(bp_df: pd.DataFrame, dim_date_df: pd.DataFrame) -> bool:
        """
        Validate that business plan and date dimension data are compatible.
        
        Args:
            bp_df: Business plan DataFrame
            dim_date_df: Date dimension DataFrame
        
        Returns:
            True if data is compatible, False otherwise
        
        Raises:
            ValueError: If data is incompatible
        """
        # Check if all business plan year/month combinations exist in date dimension
        bp_years_months = set(zip(bp_df['year'], bp_df['month']))
        dim_years_months = set(zip(dim_date_df['year'], dim_date_df['month']))
        
        missing_combinations = bp_years_months - dim_years_months
        if missing_combinations:
            raise ValueError(f"Missing date dimension data for year/month combinations: {missing_combinations}")
        
        return True
    
    @staticmethod
    def get_month_dates(dim_date_df: pd.DataFrame, year: int, month: int) -> pd.DataFrame:
        """
        Get dates for a specific year and month.
        
        Args:
            dim_date_df: Date dimension DataFrame
            year: Year to filter
            month: Month to filter
        
        Returns:
            DataFrame with dates for the specified year/month
        """
        month_dates = dim_date_df[
            (dim_date_df['year'] == year) & 
            (dim_date_df['month'] == month)
        ].copy().sort_values('persian_date')
        
        if len(month_dates) == 0:
            raise ValueError(f"No dates found for year {year}, month {month}")
        
        return month_dates
    
    @staticmethod
    def get_unique_metrics(bp_df: pd.DataFrame) -> pd.DataFrame:
        """
        Get unique line/metric/sub_metric combinations.
        
        Args:
            bp_df: Business plan DataFrame
        
        Returns:
            DataFrame with unique combinations
        """
        return bp_df[['line', 'metric', 'sub_metric']].drop_duplicates()
    
    @staticmethod
    def filter_by_metric(bp_df: pd.DataFrame, line: str, metric: str, sub_metric: str) -> pd.DataFrame:
        """
        Filter business plan by specific line/metric/sub_metric.
        
        Args:
            bp_df: Business plan DataFrame
            line: Line to filter
            metric: Metric to filter
            sub_metric: Sub-metric to filter
        
        Returns:
            Filtered DataFrame
        """
        return bp_df[
            (bp_df['line'] == line) & 
            (bp_df['metric'] == metric) & 
            (bp_df['sub_metric'] == sub_metric)
        ]
    
    @staticmethod
    def get_monthly_targets(bp_df: pd.DataFrame) -> list:
        """
        Get list of monthly targets in order.
        
        Args:
            bp_df: Business plan DataFrame
        
        Returns:
            List of monthly targets
        """
        # Sort by year, month, line, metric, sub_metric
        sorted_bp = bp_df.sort_values(['year', 'month', 'line', 'metric', 'sub_metric'])
        return sorted_bp['target'].tolist() 