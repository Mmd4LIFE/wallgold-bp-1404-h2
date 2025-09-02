# Daily Target Breakdown System

A professional, object-oriented system for breaking down monthly targets into daily targets with configurable weekly and monthly seasonality coefficients.

## 🚀 Features

- **Multiple Calculation Methods**: Original vs Regression-based approaches
- **Configurable Seasonality**: Weekly and monthly patterns with custom coefficients
- **Professional Charts**: Interactive Plotly visualizations with professional styling
- **Comprehensive Analysis**: Quality metrics, smoothness analysis, and validation
- **Clean Architecture**: Modular OOP design with separation of concerns
- **Flexible Configuration**: Easy customization of parameters and patterns

## 📁 Project Structure

```
daily_breakdown_system/
├── __init__.py              # Package initialization
├── config.py               # Configuration management
├── calculator.py            # Core calculation logic
├── data_loader.py           # Data loading and preprocessing
├── chart_generator.py       # Chart generation
└── system.py               # Main system orchestration

main.py                     # Main application entry point
README.md                   # This file
```

## 🏗️ Architecture

### Core Classes

#### `DailyBreakdownConfig`
- Manages all configuration parameters
- Predefined weekly and monthly coefficient patterns
- Custom coefficient management
- Regression window configuration

#### `DailyBreakdownCalculator`
- Main calculation engine
- Weekly and monthly seasonality application
- Growth curve calculation
- Regression-based growth (when enabled)

#### `RegressionGrowthCalculator`
- Calculates growth rates using sliding windows
- Linear regression on log-transformed data
- Weighted averaging of multiple windows
- Bounded growth rate application

#### `DataLoader`
- Data loading and validation
- Business plan and date dimension processing
- Data compatibility checks
- Utility functions for data filtering

#### `ChartGenerator`
- Professional Plotly chart creation
- Interactive visualizations
- Comparison charts
- Summary statistics charts

#### `DailyBreakdownSystem`
- Main orchestrator class
- High-level interface for all operations
- Complete analysis workflow
- Results saving and chart generation

## 🎯 Calculation Methods

### 1. Original Method
- **Weekly Pattern**: Custom weekend-heavy coefficients
- **Monthly Pattern**: Salary cycle coefficients
- **Growth**: Smooth growth curve with gentle acceleration
- **Use Case**: When you want specific business patterns

### 2. Regression-Based Methods
- **Regression (30)**: 30-day window only
- **Regression (30,7)**: 30-day and 7-day windows
- **Regression (30,7,2)**: 30-day, 7-day, and 2-day windows
- **Use Case**: When you want data-driven growth patterns

## 📊 Usage Examples

### Basic Usage

```python
from daily_breakdown_system import DailyBreakdownSystem

# Initialize system
system = DailyBreakdownSystem()

# Run complete analysis
analysis = system.run_complete_analysis(
    weekly_pattern='default',
    monthly_pattern='default',
    use_regression=True,
    regression_windows=[30, 7],
    save_results=True,
    create_chart=True
)
```

### Custom Configuration

```python
from daily_breakdown_system import DailyBreakdownConfig, DailyBreakdownSystem

# Create custom configuration
config = DailyBreakdownConfig()

# Set custom weekly coefficients
config.set_weekly_coefficients(
    [1.2, 1.3, 0.8, 0.85, 0.9, 0.85, 1.15],  # Weekend heavy
    'custom_weekend'
)

# Set custom monthly coefficients
config.set_monthly_coefficients(
    [1.3] * 5 + [1.15] * 5 + [0.95] * 10 + [0.85] * 5 + [0.75] * 6,  # Salary cycle
    'custom_salary'
)

# Initialize system with custom config
system = DailyBreakdownSystem(config)
```

### Command Line Usage

```bash
# Generate all methods
python main.py --all

# Run single method example
python main.py --single

# Run specific method
python main.py --method regression_30_7

# Run original method
python main.py --method original
```

## 📈 Output Files

### CSV Files (data/)
- `daily_breakdown_analysis_{method}_dt{timestamp}.csv`
- `methods_comparison_summary_dt{timestamp}.csv`

### HTML Charts (charts/)
- `daily_breakdown_analysis_{method}_dt{timestamp}.html`

## 🔧 Configuration Options

### Weekly Patterns
- `default`: Balanced business week
- `business_focused`: Higher weekday values
- `weekend_heavy`: Higher weekend values
- `balanced`: Equal weights for all days

### Monthly Patterns
- `default`: Gentle monthly progression
- `salary_cycle`: Higher values at month start
- `month_end_heavy`: Higher values at month end
- `balanced`: Equal weights for all days

### Regression Parameters
- `regression_windows`: List of window sizes (e.g., [30, 7, 2])
- `min_growth_rate`: Minimum daily growth rate (default: 0.001)
- `max_growth_rate`: Maximum daily growth rate (default: 0.05)
- `regression_smoothing`: Smoothing factor for regression results

## 📊 Analysis Metrics

### Quality Metrics
- **Min/Max Daily Targets**: Range of daily target values
- **Mean/Std Daily Targets**: Central tendency and variability
- **Smooth Days %**: Percentage of days with <5% change
- **Average Day Change %**: Average day-to-day percentage change
- **Maximum Day Change %**: Maximum day-to-day percentage change

### Validation Metrics
- **Average Difference %**: Average deviation from monthly targets
- **Max Difference %**: Maximum deviation from monthly targets
- **Validation**: Ensures daily totals match monthly targets

## 🎨 Chart Features

### Professional Styling
- Clean, modern design with professional color palette
- Responsive layout with automatic subplot arrangement
- Interactive hover labels with detailed information
- Professional borders and grid styling

### Chart Types
- **Daily Target Charts**: Line charts with markers for each metric
- **Comparison Charts**: Multiple methods on same chart
- **Summary Charts**: Bar charts for key statistics

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd daily-breakdown-system
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install pandas numpy scipy plotly
   ```

4. **Run the system**
   ```bash
   python main.py --all
   ```

## 📋 Requirements

- Python 3.8+
- pandas
- numpy
- scipy
- plotly

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions or issues, please open an issue on GitHub or contact the development team.

---

**Version**: 1.0.0  
**Author**: Daily Breakdown System  
**Last Updated**: September 2025 