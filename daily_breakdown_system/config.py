"""
Configuration module for Daily Breakdown System.
Handles all configuration parameters and coefficient management.
"""

from typing import List, Dict, Optional
import numpy as np


class DailyBreakdownConfig:
    """
    Configuration class for daily breakdown parameters.
    
    This class manages all configuration parameters including:
    - Weekly and monthly seasonality coefficients
    - Growth parameters and smoothing factors
    - Regression window configurations
    - Default patterns and custom coefficient sets
    """
    
    def __init__(self):
        """Initialize configuration with default parameters."""
        
        # Weekly coefficients (Saturday=0, Friday=6)
        # Higher values = higher daily targets for that day
        self.weekly_coefficients = {
            'default': [0.85, 0.90, 0.95, 1.05, 1.10, 1.10, 0.85],  # Sat, Sun, Mon, Tue, Wed, Thu, Fri
            'business_focused': [0.70, 0.80, 1.15, 1.20, 1.25, 1.20, 0.70],
            'weekend_heavy': [1.20, 1.30, 0.80, 0.85, 0.90, 0.85, 1.15],
            'balanced': [1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00]
        }
        
        # Monthly coefficients (day 1-31)
        # Higher values = higher daily targets for that day of month
        self.monthly_coefficients = {
            'default': self._generate_default_monthly_coefficients(),
            'salary_cycle': self._generate_salary_cycle_coefficients(),
            'month_end_heavy': self._generate_month_end_heavy_coefficients(),
            'balanced': [1.0] * 31  # All days equal
        }
        
        # Growth parameters
        self.growth_rate = 0.012  # 1.2% daily growth
        self.growth_smoothing = 0.5
        
        # Smoothing parameters
        self.weekly_smoothing = 0.3
        self.monthly_smoothing = 0.4
        
        # Regression-based growth parameters
        self.regression_windows = [30, 7]  # Default: 30-day and 7-day windows
        self.regression_smoothing = 0.3
        self.min_growth_rate = 0.001  # Minimum 0.1% daily growth
        self.max_growth_rate = 0.05   # Maximum 5% daily growth
    
    def _generate_default_monthly_coefficients(self) -> List[float]:
        """Generate default monthly coefficients with gentle patterns."""
        coefficients = []
        for day in range(1, 32):
            day_position = (day - 1) / 30  # Normalize to 0-1
            
            if day_position < 0.25:  # First quarter
                weight = 0.90 + (day_position * 0.4)  # 0.90 to 1.00
            elif day_position < 0.5:  # Second quarter
                weight = 1.00 + (day_position - 0.25) * 0.4  # 1.00 to 1.10
            elif day_position < 0.75:  # Third quarter
                weight = 1.05 - (day_position - 0.5) * 0.2  # 1.05 to 1.00
            else:  # Last quarter
                weight = 1.00 - (day_position - 0.75) * 0.2  # 1.00 to 0.95
            
            coefficients.append(weight)
        return coefficients
    
    def _generate_salary_cycle_coefficients(self) -> List[float]:
        """Generate coefficients based on salary cycle (higher at month start)."""
        coefficients = []
        for day in range(1, 32):
            if day <= 5:  # First 5 days (salary days)
                weight = 1.30
            elif day <= 10:  # Days 6-10
                weight = 1.15
            elif day <= 20:  # Days 11-20
                weight = 0.95
            elif day <= 25:  # Days 21-25
                weight = 0.85
            else:  # Last days
                weight = 0.75
            coefficients.append(weight)
        return coefficients
    
    def _generate_month_end_heavy_coefficients(self) -> List[float]:
        """Generate coefficients with higher values at month end."""
        coefficients = []
        for day in range(1, 32):
            day_position = (day - 1) / 30  # Normalize to 0-1
            
            if day_position < 0.3:  # First 30%
                weight = 0.80 + (day_position * 0.4)  # 0.80 to 0.92
            elif day_position < 0.7:  # Middle 40%
                weight = 0.92 + (day_position - 0.3) * 0.2  # 0.92 to 1.00
            else:  # Last 30%
                weight = 1.00 + (day_position - 0.7) * 0.5  # 1.00 to 1.15
            
            coefficients.append(weight)
        return coefficients
    
    def set_weekly_coefficients(self, coefficients: List[float], pattern_name: str = 'custom') -> None:
        """
        Set custom weekly coefficients.
        
        Args:
            coefficients: List of 7 coefficients (Saturday to Friday)
            pattern_name: Name for the pattern
        """
        if len(coefficients) != 7:
            raise ValueError("Weekly coefficients must have exactly 7 values (Saturday to Friday)")
        self.weekly_coefficients[pattern_name] = coefficients
    
    def set_monthly_coefficients(self, coefficients: List[float], pattern_name: str = 'custom') -> None:
        """
        Set custom monthly coefficients.
        
        Args:
            coefficients: List of 29-31 coefficients (days of month)
            pattern_name: Name for the pattern
        """
        if len(coefficients) < 29 or len(coefficients) > 31:
            raise ValueError("Monthly coefficients must have 29-31 values")
        self.monthly_coefficients[pattern_name] = coefficients
    
    def set_regression_windows(self, windows: List[int]) -> None:
        """
        Set regression windows for growth calculation.
        
        Args:
            windows: List of window sizes (e.g., [30, 7, 2])
        """
        if not all(isinstance(w, int) and w > 0 for w in windows):
            raise ValueError("All regression windows must be positive integers")
        self.regression_windows = sorted(windows, reverse=True)  # Sort descending
    
    def get_weekly_coefficients(self, pattern_name: str = 'default') -> List[float]:
        """Get weekly coefficients for specified pattern."""
        return self.weekly_coefficients.get(pattern_name, self.weekly_coefficients['default'])
    
    def get_monthly_coefficients(self, pattern_name: str = 'default') -> List[float]:
        """Get monthly coefficients for specified pattern."""
        return self.monthly_coefficients.get(pattern_name, self.monthly_coefficients['default'])
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary for serialization."""
        return {
            'weekly_coefficients': self.weekly_coefficients,
            'monthly_coefficients': self.monthly_coefficients,
            'growth_rate': self.growth_rate,
            'growth_smoothing': self.growth_smoothing,
            'weekly_smoothing': self.weekly_smoothing,
            'monthly_smoothing': self.monthly_smoothing,
            'regression_windows': self.regression_windows,
            'regression_smoothing': self.regression_smoothing,
            'min_growth_rate': self.min_growth_rate,
            'max_growth_rate': self.max_growth_rate
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'DailyBreakdownConfig':
        """Create configuration from dictionary."""
        config = cls()
        for key, value in config_dict.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config 