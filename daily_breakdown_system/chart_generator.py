"""
Chart generator module for Daily Breakdown System.
Handles creation of professional Plotly charts and visualizations.
"""

from typing import Optional
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots


class ChartGenerator:
    """
    Chart generation class using Plotly.
    
    This class creates professional, interactive charts for daily target breakdowns
    with customizable styling and layout options.
    """
    
    def __init__(self):
        """Initialize chart generator with professional color palette."""
        # Professional color palette
        self.colors = {
            'primary': "#2563eb",         # Blue-600
            'primary_dark': "#1e293b",    # Slate-800
            'primary_light': "#e0e7ef",   # Blue-100
            'primary_transparent': "rgba(37, 99, 235, 0.13)",
            'secondary': "#64748b",       # Slate-500
            'success': "#059669",         # Emerald-600
            'warning': "#d97706",         # Amber-600
            'error': "#dc2626"            # Red-600
        }
    
    def create_daily_target_chart(self, daily_breakdown: pd.DataFrame, 
                                output_file: str, method_name: str = "") -> None:
        """
        Create comprehensive daily target breakdown chart.
        
        Args:
            daily_breakdown: DataFrame with daily breakdown data
            output_file: Path to save the HTML chart
            method_name: Name of the method for chart title
        """
        
        # Prepare unique triples for subplots
        line_metric_submetric_triples = daily_breakdown[["line", "metric", "sub_metric"]].drop_duplicates().values
        n_triples = len(line_metric_submetric_triples)
        
        # Calculate subplot layout
        max_rows_per_page = 4
        n_cols = 2 if n_triples > max_rows_per_page else 1
        n_rows = (n_triples + n_cols - 1) // n_cols
        
        def make_subplot_title(line: str, metric: str, sub_metric: str) -> str:
            """Create subplot title with proper formatting."""
            return (
                f"<b>{line.title()}</b><br>"
                f"<span style='font-size:15px'><b>{metric.upper()}</b></span><br>"
                f"<span style='font-size:13px'>{sub_metric.title()}</span>"
            )
        
        # Create subplots
        fig = make_subplots(
            rows=n_rows, cols=n_cols,
            shared_xaxes=False,
            subplot_titles=[
                make_subplot_title(line, metric, sub_metric)
                for line, metric, sub_metric in line_metric_submetric_triples
            ],
            vertical_spacing=0.09,
            horizontal_spacing=0.10
        )
        
        # Add traces for each metric
        for idx, (line, metric, sub_metric) in enumerate(line_metric_submetric_triples):
            row = idx // n_cols + 1
            col = idx % n_cols + 1
            
            df = daily_breakdown[
                (daily_breakdown["line"] == line) &
                (daily_breakdown["metric"] == metric) &
                (daily_breakdown["sub_metric"] == sub_metric)
            ].copy()
            
            # Convert units if needed
            y = df["daily_target"]
            y_label = "Daily Target"
            if metric == "gmv" and df["unit"].iloc[0] == "milli_grams":
                y = y / 1_000_000  # Convert milli_grams to kg
                y_label = "Daily Target (kg)"
            
            fig.add_trace(
                go.Scatter(
                    x=df["date_string"],
                    y=y,
                    mode='lines+markers',
                    name=f"{line.title()} - {metric.upper()} - {sub_metric.title()}",
                    marker=dict(size=7, color=self.colors['primary'], 
                               line=dict(width=1, color=self.colors['primary_dark'])),
                    line=dict(width=3, color=self.colors['primary']),
                    hoverlabel=dict(bgcolor=self.colors['primary_light'], 
                                   font_size=14, font_family="Arial"),
                ),
                row=row, col=col
            )
            
            # Update axes
            fig.update_yaxes(
                title_text=y_label, 
                row=row, col=col, 
                showgrid=True, 
                zeroline=True, 
                gridcolor=self.colors['primary_transparent'],
                zerolinecolor=self.colors['primary_dark'],
                tickfont=dict(color=self.colors['primary_dark'], size=13),
                title_font=dict(color=self.colors['primary_dark'], size=15)
            )
            fig.update_xaxes(
                title_text="Date", 
                row=row, col=col, 
                tickangle=45, 
                showgrid=True, 
                gridcolor=self.colors['primary_transparent'],
                tickfont=dict(color=self.colors['primary_dark'], size=13),
                title_font=dict(color=self.colors['primary_dark'], size=15)
            )
        
        # Update layout
        title_text = f"<b style='color:#2563eb'>Daily Target Breakdown"
        if method_name:
            title_text += f" - {method_name}"
        title_text += "</b>"
        
        fig.update_layout(
            height=370 * n_rows,
            width=950 if n_cols == 1 else 1800,
            showlegend=False,
            title_text=title_text,
            title_font_size=20,
            font=dict(family="Segoe UI, Arial, sans-serif", size=16, 
                     color=self.colors['primary_dark']),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=80, r=80, t=100, b=70),
            hoverlabel=dict(bgcolor=self.colors['primary_light'], 
                           font_size=14, font_family="Arial"),
            separators=","
        )
        
        # Add professional border
        fig.add_shape(
            type="rect",
            xref="paper", yref="paper",
            x0=0, y0=0, x1=1, y1=1,
            line=dict(color=self.colors['primary'], width=3),
            layer="below"
        )
        
        # Save chart
        fig.write_html(output_file)
        print(f"Chart saved to: {output_file}")
    
    def create_comparison_chart(self, daily_breakdowns: dict, output_file: str) -> None:
        """
        Create comparison chart for multiple methods.
        
        Args:
            daily_breakdowns: Dictionary of {method_name: DataFrame}
            output_file: Path to save the HTML chart
        """
        
        # Get the first DataFrame to determine metrics
        first_df = list(daily_breakdowns.values())[0]
        line_metric_submetric_triples = first_df[["line", "metric", "sub_metric"]].drop_duplicates().values
        
        # Create subplots
        n_triples = len(line_metric_submetric_triples)
        n_cols = 2 if n_triples > 2 else 1
        n_rows = (n_triples + n_cols - 1) // n_cols
        
        fig = make_subplots(
            rows=n_rows, cols=n_cols,
            shared_xaxes=False,
            subplot_titles=[
                f"{line.title()} - {metric.upper()} - {sub_metric.title()}"
                for line, metric, sub_metric in line_metric_submetric_triples
            ],
            vertical_spacing=0.09,
            horizontal_spacing=0.10
        )
        
        # Color palette for different methods
        method_colors = {
            'Original Method': self.colors['error'],
            'Regression (30)': self.colors['primary'],
            'Regression (30,7)': self.colors['success'],
            'Regression (30,7,2)': self.colors['warning']
        }
        
        # Add traces for each method and metric
        for idx, (line, metric, sub_metric) in enumerate(line_metric_submetric_triples):
            row = idx // n_cols + 1
            col = idx % n_cols + 1
            
            for method_name, df in daily_breakdowns.items():
                method_df = df[
                    (df["line"] == line) &
                    (df["metric"] == metric) &
                    (df["sub_metric"] == sub_metric)
                ].copy()
                
                if len(method_df) == 0:
                    continue
                
                # Convert units if needed
                y = method_df["daily_target"]
                if metric == "gmv" and method_df["unit"].iloc[0] == "milli_grams":
                    y = y / 1_000_000  # Convert milli_grams to kg
                
                color = method_colors.get(method_name, self.colors['secondary'])
                
                fig.add_trace(
                    go.Scatter(
                        x=method_df["date_string"],
                        y=y,
                        mode='lines+markers',
                        name=f"{method_name} - {line.title()} - {metric.upper()} - {sub_metric.title()}",
                        marker=dict(size=5, color=color),
                        line=dict(width=2, color=color),
                        showlegend=True,
                    ),
                    row=row, col=col
                )
            
            # Update axes
            y_label = "Daily Target"
            if metric == "gmv":
                y_label = "Daily Target (kg)"
            
            fig.update_yaxes(
                title_text=y_label, 
                row=row, col=col, 
                showgrid=True, 
                zeroline=True, 
                gridcolor=self.colors['primary_transparent'],
                zerolinecolor=self.colors['primary_dark'],
                tickfont=dict(color=self.colors['primary_dark'], size=13),
                title_font=dict(color=self.colors['primary_dark'], size=15)
            )
            fig.update_xaxes(
                title_text="Date", 
                row=row, col=col, 
                tickangle=45, 
                showgrid=True, 
                gridcolor=self.colors['primary_transparent'],
                tickfont=dict(color=self.colors['primary_dark'], size=13),
                title_font=dict(color=self.colors['primary_dark'], size=15)
            )
        
        # Update layout
        fig.update_layout(
            height=370 * n_rows,
            width=950 if n_cols == 1 else 1800,
            showlegend=True,
            title_text="<b style='color:#2563eb'>Daily Target Breakdown - Method Comparison</b>",
            title_font_size=20,
            font=dict(family="Segoe UI, Arial, sans-serif", size=16, 
                     color=self.colors['primary_dark']),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=80, r=80, t=100, b=70),
            hoverlabel=dict(bgcolor=self.colors['primary_light'], 
                           font_size=14, font_family="Arial"),
            separators=","
        )
        
        # Add professional border
        fig.add_shape(
            type="rect",
            xref="paper", yref="paper",
            x0=0, y0=0, x1=1, y1=1,
            line=dict(color=self.colors['primary'], width=3),
            layer="below"
        )
        
        # Save chart
        fig.write_html(output_file)
        print(f"Comparison chart saved to: {output_file}")
    
    def create_summary_chart(self, summary_data: pd.DataFrame, output_file: str) -> None:
        """
        Create summary chart showing key metrics comparison.
        
        Args:
            summary_data: DataFrame with summary statistics
            output_file: Path to save the HTML chart
        """
        
        # Create bar chart for key metrics
        fig = go.Figure()
        
        # Add bars for different metrics
        metrics = ['min_daily_target', 'max_daily_target', 'mean_daily_target', 'std_daily_target']
        metric_names = ['Min Target', 'Max Target', 'Mean Target', 'Std Dev']
        
        for i, (metric, name) in enumerate(zip(metrics, metric_names)):
            fig.add_trace(go.Bar(
                name=name,
                x=summary_data['method_name'],
                y=summary_data[metric],
                marker_color=self.colors['primary'] if i == 0 else self.colors['secondary']
            ))
        
        # Update layout
        fig.update_layout(
            title="<b style='color:#2563eb'>Daily Target Statistics Comparison</b>",
            title_font_size=20,
            xaxis_title="Method",
            yaxis_title="Value",
            barmode='group',
            font=dict(family="Segoe UI, Arial, sans-serif", size=14),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=80, r=80, t=100, b=80)
        )
        
        # Save chart
        fig.write_html(output_file)
        print(f"Summary chart saved to: {output_file}") 