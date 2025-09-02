"""
Daily Target Breakdown System
A professional system for breaking down monthly targets into daily targets
with configurable weekly and monthly seasonality coefficients.
"""

from .config import DailyBreakdownConfig
from .calculator import DailyBreakdownCalculator, RegressionGrowthCalculator
from .data_loader import DataLoader
from .chart_generator import ChartGenerator
from .system import DailyBreakdownSystem

__version__ = "1.0.0"
__author__ = "Daily Breakdown System"

__all__ = [
    'DailyBreakdownConfig',
    'DailyBreakdownCalculator', 
    'RegressionGrowthCalculator',
    'DataLoader',
    'ChartGenerator',
    'DailyBreakdownSystem'
] 