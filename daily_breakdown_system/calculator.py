"""
Calculator module for Daily Breakdown System.
Contains the main calculation logic and regression growth calculator.
"""

from typing import List, Dict, Tuple, Optional
import pandas as pd
import numpy as np
from scipy import stats
from .config import DailyBreakdownConfig


class RegressionGrowthCalculator:
    """
    Calculate growth rates using regression on sliding windows.
    
    This class implements regression-based growth calculation using
    multiple time windows to capture different trends.
    """
    
    def __init__(self, config: DailyBreakdownConfig):
        """
        Initialize regression calculator.
        
        Args:
            config: Configuration object with regression parameters
        """
        self.config = config
    
    def calculate_regression_growth(self, monthly_targets: List[float], 
                                 current_month_index: int) -> float:
        """
        Calculate growth rate using regression on sliding windows.
        
        Args:
            monthly_targets: List of monthly targets (historical + current)
            current_month_index: Index of current month in the list
        
        Returns:
            Calculated growth rate
        """
        if len(monthly_targets) < 2:
            return self.config.growth_rate  # Default if not enough data
        
        # Calculate growth rates for each window
        growth_rates = []
        
        for window_size in self.config.regression_windows:
            if current_month_index >= window_size - 1:
                # Get data for this window
                window_data = monthly_targets[current_month_index - window_size + 1:current_month_index + 1]
                
                if len(window_data) >= 2:
                    # Calculate growth rate using linear regression
                    x = np.arange(len(window_data))
                    y = np.log(window_data)  # Use log for exponential growth
                    
                    # Linear regression
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                    
                    # Convert slope to daily growth rate
                    daily_growth = np.exp(slope) - 1
                    
                    # Apply bounds
                    daily_growth = max(self.config.min_growth_rate, 
                                     min(self.config.max_growth_rate, daily_growth))
                    
                    growth_rates.append(daily_growth)
        
        # If no valid growth rates, use default
        if not growth_rates:
            return self.config.growth_rate
        
        # Weighted average based on window size (larger windows get more weight)
        total_weight = sum(self.config.regression_windows[:len(growth_rates)])
        weighted_growth = sum(growth_rate * weight for growth_rate, weight in 
                           zip(growth_rates, self.config.regression_windows[:len(growth_rates)]))
        
        return weighted_growth / total_weight
    
    def apply_regression_growth_curve(self, days_in_month: int, 
                                    growth_rate: float) -> List[float]:
        """
        Apply regression-based growth curve with smooth transitions.
        
        Args:
            days_in_month: Number of days in the month
            growth_rate: Calculated growth rate
        
        Returns:
            List of growth factors for each day
        """
        growth_curve = []
        
        for day in range(days_in_month):
            # Use a more conservative growth pattern
            normalized_day = day / days_in_month
            
            # Smooth growth pattern: starts moderate, accelerates gently, then stabilizes
            if normalized_day < 0.2:  # First 20%
                # Gentle start
                growth_factor = 1 + (growth_rate * 0.5) * normalized_day * 5
            elif normalized_day < 0.6:  # Middle 40%
                # Moderate acceleration
                mid_point = (normalized_day - 0.2) / 0.4
                growth_factor = 1 + (growth_rate * 0.8) * (0.5 + mid_point * 0.5)
            elif normalized_day < 0.9:  # Last 30% (excluding last 10%)
                # Gentle stabilization
                end_point = (normalized_day - 0.6) / 0.3
                growth_factor = 1 + (growth_rate * 0.6) * (0.8 + end_point * 0.2)
            else:  # Last 10%
                # Very gentle finish
                final_point = (normalized_day - 0.9) / 0.1
                growth_factor = 1 + (growth_rate * 0.3) * (0.9 + final_point * 0.1)
            
            growth_curve.append(growth_factor)
        
        # Apply smoothing
        smoothed_growth = self._smooth_weights(growth_curve, self.config.regression_smoothing)
        return smoothed_growth
    
    def _smooth_weights(self, weights: List[float], smoothing_factor: float) -> List[float]:
        """Apply smoothing to weights using moving average."""
        smoothed_weights = []
        
        for i in range(len(weights)):
            if i == 0:
                smoothed = (weights[i] + weights[i+1]) / 2
            elif i == len(weights) - 1:
                smoothed = (weights[i-1] + weights[i]) / 2
            else:
                smoothed = (weights[i-1] + weights[i] + weights[i+1]) / 3
            
            final_weight = weights[i] * (1 - smoothing_factor) + smoothed * smoothing_factor
            smoothed_weights.append(final_weight)
        
        return smoothed_weights


class DailyBreakdownCalculator:
    """
    Main calculator class for daily target breakdown.
    
    This class orchestrates the entire calculation process including:
    - Weekly and monthly seasonality application
    - Growth curve calculation
    - Regression-based growth (when enabled)
    - Final target calculation and normalization
    """
    
    def __init__(self, config: DailyBreakdownConfig):
        """
        Initialize calculator.
        
        Args:
            config: Configuration object with all parameters
        """
        self.config = config
        self.regression_calculator = RegressionGrowthCalculator(config)
    
    def get_weekday_from_persian_date(self, persian_date_str: str) -> int:
        """
        Calculate weekday from Persian date (Saturday = 0, Friday = 6).
        
        Args:
            persian_date_str: Persian date string (YYYYMMDD format)
        
        Returns:
            Weekday index (0-6)
        """
        persian_date_str = str(persian_date_str)
        day = int(persian_date_str[6:8])
        return (day - 1) % 7
    
    def get_day_of_month(self, persian_date_str: str) -> int:
        """
        Get day of month from Persian date.
        
        Args:
            persian_date_str: Persian date string (YYYYMMDD format)
        
        Returns:
            Day of month (1-31)
        """
        persian_date_str = str(persian_date_str)
        return int(persian_date_str[6:8])
    
    def apply_weekly_seasonality(self, weekdays: List[int], 
                                pattern_name: str = 'default') -> List[float]:
        """
        Apply weekly seasonality coefficients.
        
        Args:
            weekdays: List of weekday indices (0-6)
            pattern_name: Name of weekly pattern to use
        
        Returns:
            List of weekly seasonality weights
        """
        coefficients = self.config.get_weekly_coefficients(pattern_name)
        weights = [coefficients[weekday] for weekday in weekdays]
        
        # Apply smoothing
        smoothed_weights = self._smooth_weights(weights, self.config.weekly_smoothing)
        return smoothed_weights
    
    def apply_monthly_seasonality(self, days_in_month: int, 
                                 pattern_name: str = 'default') -> List[float]:
        """
        Apply monthly seasonality coefficients.
        
        Args:
            days_in_month: Number of days in the month
            pattern_name: Name of monthly pattern to use
        
        Returns:
            List of monthly seasonality weights
        """
        coefficients = self.config.get_monthly_coefficients(pattern_name)
        
        # Adjust coefficients for actual days in month
        if days_in_month <= len(coefficients):
            monthly_weights = coefficients[:days_in_month]
        else:
            # Extend coefficients if needed
            monthly_weights = coefficients + [1.0] * (days_in_month - len(coefficients))
        
        # Apply smoothing
        smoothed_weights = self._smooth_weights(monthly_weights, self.config.monthly_smoothing)
        return smoothed_weights
    
    def apply_growth_curve(self, days_in_month: int) -> List[float]:
        """
        Apply growth curve with smooth acceleration.
        
        Args:
            days_in_month: Number of days in the month
        
        Returns:
            List of growth factors for each day
        """
        growth_curve = []
        
        for day in range(days_in_month):
            normalized_day = day / days_in_month
            
            # Smooth growth: starts slow, accelerates smoothly, then stabilizes
            if normalized_day < 0.3:  # First 30%
                growth_factor = 1 + (self.config.growth_rate * 0.3) * normalized_day * 10
            elif normalized_day < 0.7:  # Middle 40%
                mid_point = (normalized_day - 0.3) / 0.4
                growth_factor = 1 + (self.config.growth_rate * 0.8) * (0.3 + mid_point * 0.7)
            else:  # Last 30%
                end_point = (normalized_day - 0.7) / 0.3
                growth_factor = 1 + (self.config.growth_rate * 0.6) * (0.8 + end_point * 0.2)
            
            growth_curve.append(growth_factor)
        
        # Apply additional smoothing
        smoothed_growth = self._smooth_weights(growth_curve, self.config.growth_smoothing)
        return smoothed_growth
    
    def apply_regression_growth_curve(self, days_in_month: int, 
                                    monthly_targets: List[float], 
                                    current_month_index: int) -> List[float]:
        """
        Apply regression-based growth curve.
        
        Args:
            days_in_month: Number of days in the month
            monthly_targets: List of monthly targets
            current_month_index: Index of current month
        
        Returns:
            List of growth factors for each day
        """
        # Calculate growth rate using regression
        growth_rate = self.regression_calculator.calculate_regression_growth(
            monthly_targets, current_month_index
        )
        
        # Apply growth curve
        return self.regression_calculator.apply_regression_growth_curve(days_in_month, growth_rate)
    
    def _smooth_weights(self, weights: List[float], smoothing_factor: float) -> List[float]:
        """Apply smoothing to weights using moving average."""
        smoothed_weights = []
        
        for i in range(len(weights)):
            if i == 0:
                smoothed = (weights[i] + weights[i+1]) / 2
            elif i == len(weights) - 1:
                smoothed = (weights[i-1] + weights[i]) / 2
            else:
                smoothed = (weights[i-1] + weights[i] + weights[i+1]) / 3
            
            final_weight = weights[i] * (1 - smoothing_factor) + smoothed * smoothing_factor
            smoothed_weights.append(final_weight)
        
        return smoothed_weights
    
    def calculate_daily_targets(self, monthly_target: float, month_dates: pd.DataFrame,
                              weekly_pattern: str = 'default',
                              monthly_pattern: str = 'default',
                              use_regression: bool = False,
                              monthly_targets: Optional[List[float]] = None,
                              current_month_index: Optional[int] = None) -> List[float]:
        """
        Calculate daily targets for a given month.
        
        Args:
            monthly_target: Monthly target value
            month_dates: DataFrame with month dates
            weekly_pattern: Weekly seasonality pattern name
            monthly_pattern: Monthly seasonality pattern name
            use_regression: Whether to use regression-based growth
            monthly_targets: List of monthly targets (for regression)
            current_month_index: Current month index (for regression)
        
        Returns:
            List of daily target values
        """
        days_in_month = len(month_dates)
        
        # 1. Calculate growth curve
        if use_regression and monthly_targets is not None and current_month_index is not None:
            growth_curve = self.apply_regression_growth_curve(
                days_in_month, monthly_targets, current_month_index
            )
        else:
            growth_curve = self.apply_growth_curve(days_in_month)
        
        # 2. Calculate weekly seasonality
        weekdays = [self.get_weekday_from_persian_date(str(date_row['persian_date'])) 
                   for _, date_row in month_dates.iterrows()]
        weekly_weights = self.apply_weekly_seasonality(weekdays, weekly_pattern)
        
        # 3. Calculate monthly seasonality
        monthly_weights = self.apply_monthly_seasonality(days_in_month, monthly_pattern)
        
        # 4. Combine all factors with more balanced approach
        combined_weights = []
        for i in range(days_in_month):
            # Use arithmetic mean for more balanced combination
            combined_weight = (growth_curve[i] + weekly_weights[i] + monthly_weights[i]) / 3
            combined_weights.append(combined_weight)
        
        # 5. Apply final smoothing
        final_weights = self._smooth_weights(combined_weights, 0.1)
        
        # 6. Normalize to ensure total equals monthly target
        total_weight = sum(final_weights)
        daily_targets = [monthly_target * weight / total_weight for weight in final_weights]
        
        return daily_targets 