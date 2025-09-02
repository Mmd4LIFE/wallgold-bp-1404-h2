"""
Main system module for Daily Breakdown System.
Orchestrates the entire daily breakdown process.
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd
import os
from datetime import datetime

from .config import DailyBreakdownConfig
from .calculator import DailyBreakdownCalculator
from .data_loader import DataLoader
from .chart_generator import ChartGenerator


class DailyBreakdownSystem:
    """
    Main system class that orchestrates the entire daily breakdown process.
    
    This class provides a high-level interface for:
    - Loading and validating data
    - Creating daily breakdowns with different methods
    - Analyzing results and generating reports
    - Creating charts and visualizations
    - Saving results to files
    """
    
    def __init__(self, config: Optional[DailyBreakdownConfig] = None):
        """
        Initialize the daily breakdown system.
        
        Args:
            config: Configuration object (optional, creates default if not provided)
        """
        self.config = config or DailyBreakdownConfig()
        self.calculator = DailyBreakdownCalculator(self.config)
        self.data_loader = DataLoader()
        self.chart_generator = ChartGenerator()
        
        # Data storage
        self.bp_data = None
        self.dim_date_data = None
        
        # Create timestamp for this session
        self.session_timestamp = datetime.now().strftime("%Y%m%d%H%M")
        
        # Create organized folder structure
        self._create_session_folders()
    
    def _create_session_folders(self) -> None:
        """Create organized folder structure for this session."""
        # Create data folder with timestamp
        self.data_folder = f"data/daily_breakdown_dt{self.session_timestamp}"
        os.makedirs(self.data_folder, exist_ok=True)
        
        # Create charts folder with timestamp
        self.charts_folder = f"charts/daily_breakdown_dt{self.session_timestamp}"
        os.makedirs(self.charts_folder, exist_ok=True)
        
        print(f"📁 Session folders created:")
        print(f"   📊 Data: {self.data_folder}")
        print(f"   📈 Charts: {self.charts_folder}")
    
    def load_data(self, bp_file: str = "data/bp - Structured.csv", 
                  dim_date_file: str = "data/gold_dw_public_dim_date.csv") -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load and validate data.
        
        Args:
            bp_file: Path to business plan CSV file
            dim_date_file: Path to date dimension CSV file
        
        Returns:
            Tuple of (business_plan_df, date_dimension_df)
        
        Raises:
            FileNotFoundError: If data files don't exist
            ValueError: If data is invalid or incompatible
        """
        print("Loading data...")
        
        # Load data
        self.bp_data = self.data_loader.load_business_plan(bp_file)
        self.dim_date_data = self.data_loader.load_date_dimension(dim_date_file)
        
        # Validate compatibility
        self.data_loader.validate_data_compatibility(self.bp_data, self.dim_date_data)
        
        print(f"Business plan records: {len(self.bp_data)}")
        print(f"Date dimension records: {len(self.dim_date_data)}")
        
        return self.bp_data, self.dim_date_data
    
    def create_daily_breakdown(self, weekly_pattern: str = 'default',
                              monthly_pattern: str = 'default',
                              use_regression: bool = False,
                              regression_windows: Optional[List[int]] = None) -> pd.DataFrame:
        """
        Create daily breakdown with specified parameters.
        
        Args:
            weekly_pattern: Weekly seasonality pattern name
            monthly_pattern: Monthly seasonality pattern name
            use_regression: Whether to use regression-based growth
            regression_windows: List of regression window sizes
        
        Returns:
            DataFrame with daily breakdown data
        """
        if self.bp_data is None or self.dim_date_data is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        print(f"\nCreating daily breakdown...")
        print(f"Weekly pattern: {weekly_pattern}")
        print(f"Monthly pattern: {monthly_pattern}")
        print(f"Use regression: {use_regression}")
        
        if use_regression and regression_windows:
            self.config.set_regression_windows(regression_windows)
            print(f"Regression windows: {self.config.regression_windows}")
        
        daily_breakdown = []
        
        # Prepare monthly targets for regression (if needed)
        monthly_targets = None
        if use_regression:
            monthly_targets = self.data_loader.get_monthly_targets(self.bp_data)
        
        for idx, bp_row in self.bp_data.iterrows():
            year = bp_row['year']
            month = bp_row['month']
            monthly_target = bp_row['target']
            
            # Get month dates
            month_dates = self.data_loader.get_month_dates(self.dim_date_data, year, month)
            
            # Calculate daily targets
            daily_targets = self.calculator.calculate_daily_targets(
                monthly_target, month_dates, weekly_pattern, monthly_pattern,
                use_regression, monthly_targets, idx
            )
            
            # Create daily records
            for i, (_, date_row) in enumerate(month_dates.iterrows()):
                daily_record = {
                    'year': year,
                    'month': month,
                    'persian_date': date_row['persian_date'],
                    'date_id': date_row['date_id'],
                    'date_string': date_row['date_string'],
                    'line': bp_row['line'],
                    'metric': bp_row['metric'],
                    'sub_metric': bp_row['sub_metric'],
                    'daily_target': daily_targets[i],
                    'unit': bp_row['unit'],
                    'distribution_method': 'regression_seasonal_growth' if use_regression else 'smooth_seasonal_growth',
                    'growth_rate': self.config.growth_rate,
                    'weekly_smoothing': self.config.weekly_smoothing,
                    'monthly_smoothing': self.config.monthly_smoothing,
                    'growth_smoothing': self.config.growth_smoothing,
                    'weekly_pattern': weekly_pattern,
                    'monthly_pattern': monthly_pattern,
                    'use_regression': use_regression,
                    'regression_windows': str(self.config.regression_windows) if use_regression else None
                }
                daily_breakdown.append(daily_record)
        
        result_df = pd.DataFrame(daily_breakdown)
        print(f"Daily breakdown created: {len(result_df)} records")
        
        return result_df
    
    def analyze_breakdown(self, daily_breakdown: pd.DataFrame) -> Dict:
        """
        Analyze the breakdown for quality metrics.
        
        Args:
            daily_breakdown: DataFrame with daily breakdown data
        
        Returns:
            Dictionary with analysis results
        """
        print("\nAnalyzing breakdown...")
        
        # Calculate day-to-day changes
        daily_breakdown['day_change'] = daily_breakdown.groupby(
            ['year', 'month', 'line', 'metric', 'sub_metric']
        )['daily_target'].diff()
        daily_breakdown['day_change_pct'] = daily_breakdown.groupby(
            ['year', 'month', 'line', 'metric', 'sub_metric']
        )['daily_target'].pct_change() * 100
        
        # Calculate smoothness metrics
        smoothness_stats = {
            'avg_day_change': daily_breakdown['day_change'].abs().mean(),
            'max_day_change': daily_breakdown['day_change'].abs().max(),
            'avg_day_change_pct': daily_breakdown['day_change_pct'].abs().mean(),
            'max_day_change_pct': daily_breakdown['day_change_pct'].abs().max(),
            'smooth_days_pct': (daily_breakdown['day_change_pct'].abs() < 5).mean() * 100
        }
        
        # Validate against monthly targets
        monthly_totals = daily_breakdown.groupby(
            ['year', 'month', 'line', 'metric', 'sub_metric']
        )['daily_target'].sum().reset_index()
        monthly_totals.rename(columns={'daily_target': 'calculated_total'}, inplace=True)
        
        validation = pd.merge(
            monthly_totals, 
            self.bp_data[['year', 'month', 'line', 'metric', 'sub_metric', 'target']], 
            on=['year', 'month', 'line', 'metric', 'sub_metric']
        )
        validation['difference_percentage'] = (
            (validation['calculated_total'] - validation['target']) / validation['target']
        ) * 100
        
        validation_stats = {
            'avg_difference_pct': validation['difference_percentage'].mean(),
            'max_difference_pct': validation['difference_percentage'].max(),
            'min_difference_pct': validation['difference_percentage'].min(),
            'std_difference_pct': validation['difference_percentage'].std()
        }
        
        # Print analysis results
        print(f"Average day-to-day change: {smoothness_stats['avg_day_change']:,.0f}")
        print(f"Maximum day-to-day change: {smoothness_stats['max_day_change']:,.0f}")
        print(f"Average day-to-day change %: {smoothness_stats['avg_day_change_pct']:.2f}%")
        print(f"Maximum day-to-day change %: {smoothness_stats['max_day_change_pct']:.2f}%")
        print(f"Days with <5% change: {smoothness_stats['smooth_days_pct']:.1f}%")
        print(f"Average difference from monthly targets: {validation_stats['avg_difference_pct']:.4f}%")
        print(f"Max difference: {validation_stats['max_difference_pct']:.4f}%")
        
        return {
            'smoothness': smoothness_stats,
            'validation': validation_stats,
            'daily_breakdown': daily_breakdown
        }
    
    def save_results(self, daily_breakdown: pd.DataFrame, 
                    filename: str = "daily_breakdown.csv") -> str:
        """
        Save results to CSV file in the session data folder.
        
        Args:
            daily_breakdown: DataFrame with daily breakdown data
            filename: Name of the CSV file (without path)
        
        Returns:
            Full path to the saved file
        """
        output_file = os.path.join(self.data_folder, filename)
        daily_breakdown.to_csv(output_file, index=False)
        print(f"✅ CSV saved: {output_file}")
        return output_file
    
    def create_chart(self, daily_breakdown: pd.DataFrame, 
                    filename: str = "daily_target_breakdown.html",
                    method_name: str = "") -> str:
        """
        Create and save chart in the session charts folder.
        
        Args:
            daily_breakdown: DataFrame with daily breakdown data
            filename: Name of the HTML file (without path)
            method_name: Name of the method for chart title
        
        Returns:
            Full path to the saved file
        """
        output_file = os.path.join(self.charts_folder, filename)
        self.chart_generator.create_daily_target_chart(daily_breakdown, output_file, method_name)
        return output_file
    
    def run_complete_analysis(self, weekly_pattern: str = 'default',
                            monthly_pattern: str = 'default',
                            use_regression: bool = False,
                            regression_windows: Optional[List[int]] = None,
                            save_results: bool = True,
                            create_chart: bool = True,
                            output_prefix: str = "daily_breakdown") -> Dict:
        """
        Run complete analysis with all steps.
        
        Args:
            weekly_pattern: Weekly seasonality pattern name
            monthly_pattern: Monthly seasonality pattern name
            use_regression: Whether to use regression-based growth
            regression_windows: List of regression window sizes
            save_results: Whether to save results to CSV
            create_chart: Whether to create HTML chart
            output_prefix: Prefix for output files
        
        Returns:
            Dictionary with analysis results
        """
        print("Daily Target Breakdown System")
        print("=" * 60)
        
        # Load data if not already loaded
        if self.bp_data is None or self.dim_date_data is None:
            self.load_data()
        
        # Create breakdown
        daily_breakdown = self.create_daily_breakdown(
            weekly_pattern, monthly_pattern, use_regression, regression_windows
        )
        
        # Analyze results
        analysis = self.analyze_breakdown(daily_breakdown)
        
        # Save results
        if save_results:
            csv_filename = f"{output_prefix}.csv"
            self.save_results(analysis['daily_breakdown'], csv_filename)
        
        # Create chart
        if create_chart:
            html_filename = f"{output_prefix}.html"
            method_name = f"{'Regression' if use_regression else 'Original'} ({weekly_pattern}, {monthly_pattern})"
            self.create_chart(analysis['daily_breakdown'], html_filename, method_name)
        
        return analysis
    
    def run_multiple_methods(self, method_configs: List[Dict]) -> Dict:
        """
        Run multiple methods and compare results.
        
        Args:
            method_configs: List of method configurations
        
        Returns:
            Dictionary with results for all methods
        """
        print("Running multiple methods...")
        print("=" * 60)
        
        results = {}
        
        for config in method_configs:
            method_name = config['name']
            print(f"\n🔄 Running: {method_name}")
            
            # Create new config for this method
            method_system = DailyBreakdownSystem()
            
            # Set custom coefficients if specified
            if 'weekly_coefficients' in config:
                method_system.config.set_weekly_coefficients(
                    config['weekly_coefficients'], config.get('weekly_pattern', 'custom')
                )
            
            if 'monthly_coefficients' in config:
                method_system.config.set_monthly_coefficients(
                    config['monthly_coefficients'], config.get('monthly_pattern', 'custom')
                )
            
            # Run analysis
            analysis = method_system.run_complete_analysis(
                weekly_pattern=config.get('weekly_pattern', 'default'),
                monthly_pattern=config.get('monthly_pattern', 'default'),
                use_regression=config.get('use_regression', False),
                regression_windows=config.get('regression_windows'),
                save_results=True,
                create_chart=True,
                output_prefix=f"daily_breakdown_{method_name}"
            )
            
            results[method_name] = {
                'analysis': analysis,
                'config': config
            }
        
        return results 