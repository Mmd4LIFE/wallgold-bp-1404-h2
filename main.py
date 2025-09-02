import os
import sys
from datetime import datetime
from typing import List, Dict

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from daily_breakdown_system import (
    DailyBreakdownConfig, 
    DailyBreakdownSystem,
    ChartGenerator
)


def create_method_configurations() -> List[Dict]:
    """
    Create configurations for different calculation methods.
    
    Returns:
        List of method configurations
    """
    return [
        {
            'name': 'original',
            'display_name': 'Original Method',
            'weekly_pattern': 'custom_weekend_heavy',
            'monthly_pattern': 'custom_salary_cycle',
            'use_regression': False,
            'weekly_coefficients': [1.20, 1.30, 0.80, 0.85, 0.90, 0.85, 1.15],  # Weekend heavy
            'monthly_coefficients': [1.30, 1.30, 1.30, 1.30, 1.30, 1.15, 1.15, 1.15, 1.15, 1.15, 
                                   0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95,
                                   0.85, 0.85, 0.85, 0.85, 0.85, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75]  # Salary cycle
        },
        {
            'name': 'regression_30',
            'display_name': 'Regression (30)',
            'weekly_pattern': 'default',
            'monthly_pattern': 'default',
            'use_regression': True,
            'regression_windows': [30]
        },
        {
            'name': 'regression_30_7',
            'display_name': 'Regression (30,7)',
            'weekly_pattern': 'default',
            'monthly_pattern': 'default',
            'use_regression': True,
            'regression_windows': [30, 7]
        },
        {
            'name': 'regression_30_7_2',
            'display_name': 'Regression (30,7,2)',
            'weekly_pattern': 'default',
            'monthly_pattern': 'default',
            'use_regression': True,
            'regression_windows': [30, 7, 2]
        }
    ]


def generate_all_methods() -> None:
    """
    Generate all calculation methods and save results.
    """
    print("Daily Target Breakdown - Generate All Methods")
    print("=" * 60)
    
    # Get method configurations
    method_configs = create_method_configurations()
    
    # Initialize system (this will create timestamped folders)
    system = DailyBreakdownSystem()
    
    # Load data once
    system.load_data(
        bp_file="data/bp - Structured.csv",
        dim_date_file="data/gold_dw_public_dim_date.csv"
    )
    
    # Store results for comparison
    all_results = {}
    
    # Generate each method
    for config in method_configs:
        print(f"\n🔄 Generating: {config['display_name']}")
        print(f"   Regression: {config['use_regression']}")
        print(f"   Weekly pattern: {config['weekly_pattern']}")
        print(f"   Monthly pattern: {config['monthly_pattern']}")
        
        if config['use_regression']:
            print(f"   Windows: {config['regression_windows']}")
        
        # Create custom config if needed
        if 'weekly_coefficients' in config or 'monthly_coefficients' in config:
            custom_config = DailyBreakdownConfig()
            
            if 'weekly_coefficients' in config:
                custom_config.set_weekly_coefficients(
                    config['weekly_coefficients'], 
                    config['weekly_pattern']
                )
            
            if 'monthly_coefficients' in config:
                custom_config.set_monthly_coefficients(
                    config['monthly_coefficients'], 
                    config['monthly_pattern']
                )
            
            method_system = DailyBreakdownSystem(custom_config)
            method_system.load_data()
        else:
            method_system = system
        
        # Run analysis
        analysis = method_system.run_complete_analysis(
            weekly_pattern=config['weekly_pattern'],
            monthly_pattern=config['monthly_pattern'],
            use_regression=config['use_regression'],
            regression_windows=config.get('regression_windows'),
            save_results=True,
            create_chart=True,
            output_prefix=f"daily_breakdown_{config['name']}"
        )
        
        # Store results
        all_results[config['display_name']] = analysis
        
        # Print summary
        daily_breakdown = analysis['daily_breakdown']
        print(f"📊 Records: {len(daily_breakdown)}")
        print(f"📊 Distribution: {daily_breakdown['distribution_method'].iloc[0]}")
        if config['use_regression']:
            print(f"📊 Windows: {config['regression_windows']}")
    
    # Create summary comparison
    create_summary_comparison(all_results, system.session_timestamp)
    
    print(f"\n🎉 All methods generated successfully!")
    print(f"📁 Data folder: {system.data_folder}")
    print(f"📊 Charts folder: {system.charts_folder}")


def create_summary_comparison(all_results: Dict, timestamp: str) -> None:
    """
    Create summary comparison of all methods.
    
    Args:
        all_results: Dictionary of results for each method
        timestamp: Timestamp for file naming
    """
    print(f"\nCreating summary comparison...")
    
    # Prepare summary data
    summary_data = []
    
    for method_name, analysis in all_results.items():
        daily_breakdown = analysis['daily_breakdown']
        
        # Calculate key statistics
        stats = {
            'method_name': method_name,
            'total_records': len(daily_breakdown),
            'min_daily_target': daily_breakdown['daily_target'].min(),
            'max_daily_target': daily_breakdown['daily_target'].max(),
            'mean_daily_target': daily_breakdown['daily_target'].mean(),
            'std_daily_target': daily_breakdown['daily_target'].std(),
            'avg_day_change_pct': daily_breakdown['day_change_pct'].abs().mean(),
            'max_day_change_pct': daily_breakdown['day_change_pct'].abs().max(),
            'smooth_days_pct': (daily_breakdown['day_change_pct'].abs() < 5).mean() * 100,
            'distribution_method': daily_breakdown['distribution_method'].iloc[0],
            'use_regression': daily_breakdown['use_regression'].iloc[0],
            'weekly_pattern': daily_breakdown['weekly_pattern'].iloc[0],
            'monthly_pattern': daily_breakdown['monthly_pattern'].iloc[0],
            'regression_windows': daily_breakdown['regression_windows'].iloc[0]
        }
        
        summary_data.append(stats)
    
    # Create summary DataFrame
    import pandas as pd
    summary_df = pd.DataFrame(summary_data)
    
    # Save summary in the data folder
    summary_file = f"data/daily_breakdown_dt{timestamp}/methods_comparison_summary.csv"
    summary_df.to_csv(summary_file, index=False)
    print(f"✅ Summary saved: {summary_file}")
    
    # Print formatted comparison
    print(f"\n📋 Methods Comparison Summary:")
    print("=" * 100)
    print(f"{'Method':<20} {'Min':<12} {'Max':<12} {'Mean':<12} {'Std':<12} {'Smooth%':<8} {'Windows':<15}")
    print("-" * 100)
    
    for _, row in summary_df.iterrows():
        print(f"{row['method_name']:<20} "
              f"{row['min_daily_target']:<12,.0f} "
              f"{row['max_daily_target']:<12,.0f} "
              f"{row['mean_daily_target']:<12,.0f} "
              f"{row['std_daily_target']:<12,.0f} "
              f"{row['smooth_days_pct']:<8.1f}% "
              f"{str(row['regression_windows']) if pd.notna(row['regression_windows']) else 'N/A':<15}")
    
    # Check for differences
    print(f"\n🔍 Key Differences:")
    print("=" * 50)
    
    min_values = summary_df['min_daily_target'].values
    max_values = summary_df['max_daily_target'].values
    smooth_values = summary_df['smooth_days_pct'].values
    
    print(f"Min daily targets: {min_values}")
    if len(set(min_values)) > 1:
        print("✅ Different minimum values detected")
    else:
        print("⚠️  All methods have identical minimum values")
    
    print(f"Max daily targets: {max_values}")
    if len(set(max_values)) > 1:
        print("✅ Different maximum values detected")
    else:
        print("⚠️  All methods have identical maximum values")
    
    print(f"Smooth days %: {smooth_values}")
    if len(set(smooth_values)) > 1:
        print("✅ Different smoothness detected")
    else:
        print("⚠️  All methods have identical smoothness")


def run_single_method_example() -> None:
    """
    Run a single method example for demonstration.
    """
    print("Daily Target Breakdown System - Single Method Example")
    print("=" * 60)
    
    # Initialize system (this will create timestamped folders)
    system = DailyBreakdownSystem()
    
    # Run analysis with regression method
    analysis = system.run_complete_analysis(
        weekly_pattern='default',
        monthly_pattern='default',
        use_regression=True,
        regression_windows=[30, 7],
        save_results=True,
        create_chart=True,
        output_prefix="daily_breakdown_example"
    )
    
    print(f"\n✅ Analysis completed successfully!")
    print(f"📊 Total records: {len(analysis['daily_breakdown'])}")
    print(f"📈 Smooth days: {analysis['smoothness']['smooth_days_pct']:.1f}%")


def main():
    """
    Main entry point for the application.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Daily Target Breakdown System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --all                    # Generate all methods
  python main.py --single                 # Run single method example
  python main.py --method original        # Run specific method
  python main.py --method regression_30   # Run regression with 30-day window
        """
    )
    
    parser.add_argument(
        '--all', 
        action='store_true',
        help='Generate all calculation methods'
    )
    
    parser.add_argument(
        '--single', 
        action='store_true',
        help='Run single method example'
    )
    
    parser.add_argument(
        '--method',
        choices=['original', 'regression_30', 'regression_30_7', 'regression_30_7_2'],
        help='Run specific method'
    )
    
    args = parser.parse_args()
    
    if args.all:
        generate_all_methods()
    elif args.single:
        run_single_method_example()
    elif args.method:
        # Run specific method
        method_configs = create_method_configurations()
        config = next((c for c in method_configs if c['name'] == args.method), None)
        
        if config:
            system = DailyBreakdownSystem()
            analysis = system.run_complete_analysis(
                weekly_pattern=config['weekly_pattern'],
                monthly_pattern=config['monthly_pattern'],
                use_regression=config['use_regression'],
                regression_windows=config.get('regression_windows'),
                save_results=True,
                create_chart=True,
                output_prefix=f"daily_breakdown_{config['name']}"
            )
            print(f"\n✅ {config['display_name']} completed successfully!")
        else:
            print(f"❌ Method '{args.method}' not found")
    else:
        # Default: run all methods
        generate_all_methods()


if __name__ == "__main__":
    main() 