"""
World Bank-styled visualization functions for diff-in-diff analysis.

This module provides functions to create comparative maps and charts
for analyzing conflict and agricultural output in Ethiopia, following
World Bank data visualization standards.
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Optional, List, Tuple, Callable
from functools import wraps
import geopandas as gpd
import pandas as pd

# World Bank color palette (from wbpyplot)
WB_COLORS = {
    # Categorical colors
    'cat1': '#34A7F2',
    'cat2': '#FF9800',
    'cat3': '#664AB6',
    'cat4': '#4EC2C0',
    'cat5': '#F3578E',
    'cat6': '#081079',
    'cat7': '#0C7C68',
    'cat8': '#AA0000',
    'cat9': '#DDDA21',
    # Standard colors
    'blue': '#009FDA',
    'red': '#EB1C2D',
    'yellow': '#F7B518',
    'green': '#00AB51',
    'purple': '#872B90',
    'orange': '#F26522',
    'dark_blue': '#002244',
    'light_blue': '#5DC3E8',
    # Text and UI
    'text': '#111111',
    'text_subtle': '#666666',
    'grid': '#CED4DE',
    'gray': '#707070'
}


def apply_wb_style():
    """Apply World Bank matplotlib style settings."""
    plt.rcParams.update({
        'font.size': 14,
        'axes.titleweight': 'bold',
        'axes.titlesize': 16,
        'axes.labelsize': 14,
        'axes.labelweight': 'semibold',
        'axes.labelcolor': WB_COLORS['text'],
        'axes.edgecolor': 'none',
        'axes.grid': True,
        'axes.facecolor': 'white',
        'grid.color': WB_COLORS['grid'],
        'grid.linestyle': (0, (4, 2)),  # dashed
        'grid.linewidth': 0.85,
        'xtick.labelsize': 14,
        'xtick.color': WB_COLORS['text_subtle'],
        'xtick.direction': 'out',
        'ytick.labelsize': 14,
        'ytick.color': WB_COLORS['text_subtle'],
        'ytick.direction': 'out',
        'legend.frameon': False,
        'figure.facecolor': 'white',
        'lines.linewidth': 2.0,
    })


def wb_line_plot(
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    ylabel: Optional[str] = None,
    figsize: Tuple[float, float] = (14, 6),
    nrows: int = 1,
    ncols: int = 1,
    show_zero_line: bool = True,
    save_path: Optional[str] = None,
    dpi: int = 300
):
    """
    Decorator to apply World Bank styling to line plot functions.
    
    Supports single plots or subplots in a grid layout.
    
    Usage:
    ------
    # Single plot
    @wb_line_plot(title='My Title', ylabel='Values')
    def my_plot(ax):
        ax.plot(x, y)
    
    # Subplots (2x2 grid)
    @wb_line_plot(title='My Title', nrows=2, ncols=2, figsize=(14, 10))
    def my_plot(axes):
        axes[0, 0].plot(x, y1)
        axes[0, 1].plot(x, y2)
        axes[1, 0].plot(x, y3)
        axes[1, 1].plot(x, y4)
    
    Parameters
    ----------
    title : str, optional
        Main title for the plot
    subtitle : str, optional
        Subtitle displayed below the title
    ylabel : str, optional
        Y-axis label (applied to all subplots if grid)
    figsize : tuple of float, default (14, 6)
        Figure size (width, height) in inches
    nrows : int, default 1
        Number of subplot rows
    ncols : int, default 1
        Number of subplot columns
    show_zero_line : bool, default True
        Whether to show a horizontal line at y=0
    save_path : str, optional
        Path to save the figure
    dpi : int, default 300
        Resolution for saved figure
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Apply World Bank style
            apply_wb_style()
            
            # Create figure with subplots
            fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize, facecolor='white')
            
            # Call the plotting function
            func(axes, *args, **kwargs)
            
            # Helper function to style a single axis
            def style_axis(ax):
                # Detect if it's a timeseries (has datetime x-axis)
                is_timeseries = False
                for line in ax.get_lines():
                    if len(line.get_xdata()) > 0:
                        x_data = line.get_xdata()
                        if hasattr(x_data, 'dtype') and np.issubdtype(x_data.dtype, np.datetime64):
                            is_timeseries = True
                            break
                
                # Apply WB timeseries styling
                if is_timeseries:
                    # Remove x-axis label
                    ax.set_xlabel('')
                    
                    # Y-axis starts at 0
                    current_ylim = ax.get_ylim()
                    if current_ylim[0] > 0:
                        ax.set_ylim(bottom=0)
                    
                    # Add zero line if data crosses zero
                    if show_zero_line and current_ylim[0] < 0:
                        ax.axhline(y=0, color='#8A969F', linewidth=1, zorder=1)
                
                # Y-axis label
                if ylabel and (nrows == 1 and ncols == 1):
                    ax.set_ylabel(ylabel, fontsize=14, fontweight='semibold', color=WB_COLORS['text'])
                
                # Remove spines
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                
                # Grid styling - only horizontal lines
                ax.grid(True, axis='y', linestyle=(0, (4, 2)), linewidth=0.85, color=WB_COLORS['grid'], zorder=0)
                ax.grid(False, axis='x')
                
                # Tick parameters - remove tick marks but keep labels
                ax.tick_params(axis='both', which='both', length=0, labelsize=14)
                
                # Tick label colors
                for label in ax.get_xticklabels():
                    label.set_color(WB_COLORS['text_subtle'])
                    label.set_fontweight('regular')
                for label in ax.get_yticklabels():
                    label.set_color(WB_COLORS['text_subtle'])
                    label.set_fontweight('regular')
                
                # Legend styling
                legend = ax.get_legend()
                if legend:
                    legend.set_frame_on(False)
            
            # Apply styling to all axes
            if nrows == 1 and ncols == 1:
                style_axis(axes)
            else:
                axes_flat = axes.flatten() if isinstance(axes, np.ndarray) else [axes]
                for ax in axes_flat:
                    style_axis(ax)
            
            # Adjust layout first to get proper spacing
            plt.tight_layout()
            
            # Title and subtitle using fig.text for better positioning
            # Position title above the tight_layout area to avoid overlap
            if title or subtitle:
                # For subplots, leave more space at top
                if nrows > 1 or ncols > 1:
                    plt.subplots_adjust(top=0.90)  # Leave 10% space at top
                    title_y = 0.985
                else:
                    plt.subplots_adjust(top=0.93)
                    title_y = 0.98
                
                if title:
                    fig.text(
                        0.05, title_y,
                        title,
                        fontsize=20,
                        fontweight='bold',
                        color=WB_COLORS['text'],
                        ha='left',
                        va='top'
                    )
                    title_y -= 0.025
                
                if subtitle:
                    fig.text(
                        0.05, title_y,
                        subtitle,
                        fontsize=14,
                        color=WB_COLORS['text_subtle'],
                        ha='left',
                        va='top'
                    )
            
            # Save if path provided
            if save_path:
                plt.savefig(save_path, dpi=dpi, bbox_inches='tight', facecolor='white')
            
            return fig, axes
        
        return wrapper
    return decorator


def apply_wb_style():
    """Apply World Bank matplotlib style settings."""
    plt.rcParams.update({
        'font.size': 14,
        'axes.titleweight': 'bold',
        'axes.titlesize': 16,
        'axes.labelsize': 14,
        'axes.labelweight': 'semibold',
        'axes.labelcolor': WB_COLORS['text'],
        'axes.edgecolor': 'none',
        'axes.grid': True,
        'axes.facecolor': 'white',
        'grid.color': WB_COLORS['grid'],
        'grid.linestyle': (0, (4, 2)),  # dashed
        'grid.linewidth': 0.85,
        'xtick.labelsize': 14,
        'xtick.color': WB_COLORS['text_subtle'],
        'xtick.direction': 'out',
        'ytick.labelsize': 14,
        'ytick.color': WB_COLORS['text_subtle'],
        'ytick.direction': 'out',
        'legend.frameon': False,
        'figure.facecolor': 'white',
        'lines.linewidth': 2.0,
    })


def plot_national_indicators(merged_adm0: pd.DataFrame, 
                            title: str = 'Ethiopia National Indicators (2015-2025)',
                            subtitle: str = 'Rainfall, vegetation health, conflict events, and crop area trends',
                            figsize: Tuple[float, float] = (16, 12)) -> Tuple:
    """
    Plot national-level indicators in a 2x2 grid with pre/post 2019 statistics.
    
    Parameters
    ----------
    merged_adm0 : pd.DataFrame
        DataFrame with columns: year, rainfall_mm, EVI, nrEvents, crop_area
    title : str
        Main title for the plot
    subtitle : str
        Subtitle for the plot
    figsize : tuple
        Figure size (width, height) in inches
        
    Returns
    -------
    fig, axes : tuple
        Matplotlib figure and axes objects
    """
    # Calculate pre/post 2019 aggregates
    pre_2019 = merged_adm0[merged_adm0['year'] <= 2019]
    post_2019 = merged_adm0[merged_adm0['year'] > 2019]
    
    # Aggregates
    rainfall_pre = pre_2019['rainfall_mm'].sum()
    rainfall_post = post_2019['rainfall_mm'].sum()
    evi_pre = pre_2019['EVI'].median()
    evi_post = post_2019['EVI'].median()
    events_pre = pre_2019['nrEvents'].sum()
    events_post = post_2019['nrEvents'].sum()
    crop_pre = pre_2019['crop_area'].sum()
    crop_post = post_2019['crop_area'].sum()
    
    @wb_line_plot(
        title=title,
        subtitle=subtitle,
        nrows=2,
        ncols=2,
        figsize=figsize
    )
    def plot_indicators(axes):
        # Top left: Rainfall
        axes[0, 0].plot(merged_adm0['year'], merged_adm0['rainfall_mm'], 
                        color='#34A7F2', linewidth=2.5, marker='o', markersize=6)
        axes[0, 0].axvline(x=2019, color='#666666', linestyle='--', linewidth=1.5, alpha=0.7, zorder=1)
        axes[0, 0].set_title('Annual Rainfall', fontsize=14, fontweight='semibold', 
                             color='#111111', pad=10)
        axes[0, 0].set_ylabel('Rainfall (mm)', fontsize=12)
        axes[0, 0].set_xlim(2012, merged_adm0['year'].max())
        # Add text annotations
        axes[0, 0].text(0.05, 0.95, f'Pre-2019 Total: {rainfall_pre:,.0f} mm', 
                        transform=axes[0, 0].transAxes, fontsize=11, 
                        verticalalignment='top', color='#111111',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='none'))
        axes[0, 0].text(0.05, 0.85, f'Post-2019 Total: {rainfall_post:,.0f} mm', 
                        transform=axes[0, 0].transAxes, fontsize=11, 
                        verticalalignment='top', color='#111111',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='none'))
        
        # Top right: EVI (Vegetation Index)
        axes[0, 1].plot(merged_adm0['year'], merged_adm0['EVI'], 
                        color='#00AB51', linewidth=2.5, marker='o', markersize=6)
        axes[0, 1].axvline(x=2019, color='#666666', linestyle='--', linewidth=1.5, alpha=0.7, zorder=1)
        axes[0, 1].set_title('Enhanced Vegetation Index (EVI)', fontsize=14, fontweight='semibold', 
                             color='#111111', pad=10)
        axes[0, 1].set_ylabel('EVI', fontsize=12)
        axes[0, 1].set_xlim(2012, merged_adm0['year'].max())
        # Add text annotations
        axes[0, 1].text(0.05, 0.95, f'Pre-2019 Median: {evi_pre:.3f}', 
                        transform=axes[0, 1].transAxes, fontsize=11, 
                        verticalalignment='top', color='#111111',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='none'))
        axes[0, 1].text(0.05, 0.85, f'Post-2019 Median: {evi_post:.3f}', 
                        transform=axes[0, 1].transAxes, fontsize=11, 
                        verticalalignment='top', color='#111111',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='none'))
        
        # Bottom left: Conflict Events
        axes[1, 0].plot(merged_adm0['year'], merged_adm0['nrEvents'], 
                        color='#EB1C2D', linewidth=2.5, marker='o', markersize=6)
        axes[1, 0].axvline(x=2019, color='#666666', linestyle='--', linewidth=1.5, alpha=0.7, zorder=1)
        axes[1, 0].set_title('Conflict Events', fontsize=14, fontweight='semibold', 
                             color='#111111', pad=10)
        axes[1, 0].set_ylabel('Number of Events', fontsize=12)
        axes[1, 0].set_xlim(2012, merged_adm0['year'].max())
        # Add text annotations
        axes[1, 0].text(0.05, 0.95, f'Pre-2019 Total: {events_pre:,.0f}', 
                        transform=axes[1, 0].transAxes, fontsize=11, 
                        verticalalignment='top', color='#111111',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='none'))
        axes[1, 0].text(0.05, 0.85, f'Post-2019 Total: {events_post:,.0f}', 
                        transform=axes[1, 0].transAxes, fontsize=11, 
                        verticalalignment='top', color='#111111',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='none'))
        
        # Bottom right: Crop Area
        axes[1, 1].plot(merged_adm0['year'], merged_adm0['crop_area'], 
                        color='#FF9800', linewidth=2.5, marker='o', markersize=6)
        axes[1, 1].axvline(x=2019, color='#666666', linestyle='--', linewidth=1.5, alpha=0.7, zorder=1)
        axes[1, 1].set_title('Total Crop Area', fontsize=14, fontweight='semibold', 
                             color='#111111', pad=10)
        axes[1, 1].set_ylabel('Crop Area (hectares)', fontsize=12)
        axes[1, 1].set_xlim(2012, merged_adm0['year'].max())
        # Add text annotations
        axes[1, 1].text(0.05, 0.95, f'Pre-2019 Total: {crop_pre:,.0f} ha', 
                        transform=axes[1, 1].transAxes, fontsize=11, 
                        verticalalignment='top', color='#111111',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='none'))
        axes[1, 1].text(0.05, 0.85, f'Post-2019 Total: {crop_post:,.0f} ha', 
                        transform=axes[1, 1].transAxes, fontsize=11, 
                        verticalalignment='top', color='#111111',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='none'))
    
    return plot_indicators()


def plot_conflict_comparison(
    data: gpd.GeoDataFrame,
    column: str = 'nrEvents',
    time_categories: Tuple[str, str] = ('Pre-Conflict', 'Post-Conflict'),
    cmap: str = 'Reds',
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
    figsize: Tuple[float, float] = (14, 6),
    title: Optional[str] = None,
    boundary_gdf: Optional[gpd.GeoDataFrame] = None,
    boundary_color: str = 'black',
    boundary_linewidth: float = 1.0,
    save_path: Optional[str] = None,
    dpi: int = 300
) -> Tuple[plt.Figure, np.ndarray]:
    """
    Create side-by-side comparison maps for pre and post conflict periods.
    
    Parameters
    ----------
    data : gpd.GeoDataFrame
        GeoDataFrame containing conflict data with 'time_category' column
    column : str, default 'nrEvents'
        Column name to plot (e.g., 'nrEvents', 'nrFatalities')
    time_categories : tuple of str, default ('Pre-Conflict', 'Post-Conflict')
        Category names for the two time periods
    cmap : str, default 'Reds'
        Matplotlib colormap name
    vmin : float, optional
        Minimum value for color scale
    vmax : float, optional
        Maximum value for color scale
    figsize : tuple of float, default (14, 6)
        Figure size (width, height) in inches
    title : str, optional
        Main title for the figure
    boundary_gdf : gpd.GeoDataFrame, optional
        GeoDataFrame with boundary to overlay (e.g., country or regional boundaries)
    boundary_color : str, default 'black'
        Color for the boundary lines
    boundary_linewidth : float, default 1.0
        Width of the boundary lines
    save_path : str, optional
        Path to save the figure
    dpi : int, default 300
        Resolution for saved figure
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object
    ax : np.ndarray
        Array of axes objects
    """
    # Apply World Bank style
    apply_wb_style()
    
    # Create figure and axes
    fig, ax = plt.subplots(1, 2, figsize=figsize, facecolor='white')
    
    # Determine color scale if not provided
    if vmin is None:
        vmin = data[column].min()
    if vmax is None:
        vmax = data[column].max()
    
    # Plot pre-conflict
    pre_data = data[data['time_category'] == time_categories[0]]
    pre_data.plot(
        column=column,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        ax=ax[0],
        edgecolor='white',
        linewidth=0.2,
        legend=False
    )
    
    # Overlay boundary if provided
    if boundary_gdf is not None:
        boundary_gdf.boundary.plot(
            ax=ax[0],
            color=boundary_color,
            linewidth=boundary_linewidth
        )
    
    ax[0].set_title(
        time_categories[0],
        fontsize=14,
        fontweight='bold',
        pad=15,
        color=WB_COLORS['dark_blue']
    )
    ax[0].axis('off')
    
    # Plot post-conflict
    post_data = data[data['time_category'] == time_categories[1]]
    post_data.plot(
        column=column,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        ax=ax[1],
        edgecolor='white',
        linewidth=0.2,
        legend=True,
        legend_kwds={
            'label': column.replace('nr', 'Number of ').replace('_', ' ').title(),
            'orientation': 'vertical',
            'shrink': 0.8,
            'pad': 0.02
        }
    )
    
    # Overlay boundary if provided
    if boundary_gdf is not None:
        boundary_gdf.boundary.plot(
            ax=ax[1],
            color=boundary_color,
            linewidth=boundary_linewidth
        )
    
    ax[1].set_title(
        time_categories[1],
        fontsize=14,
        fontweight='bold',
        pad=15,
        color=WB_COLORS['dark_blue']
    )
    ax[1].axis('off')
    
    # Add main title if provided
    if title:
        fig.suptitle(
            title,
            fontsize=16,
            fontweight='bold',
            y=0.98,
            color=WB_COLORS['dark_blue']
        )
    
    # Adjust layout
    plt.tight_layout()
    
    # Add statistics annotation
    pre_total = pre_data[column].sum()
    post_total = post_data[column].sum()
    change_pct = ((post_total - pre_total) / pre_total * 100) if pre_total > 0 else 0
    
    stats_text = f"Total {column}: {time_categories[0]}: {pre_total:,.0f} | {time_categories[1]}: {post_total:,.0f} | Change: {change_pct:+.1f}%"
    fig.text(
        0.5, 0.02,
        stats_text,
        ha='center',
        fontsize=10,
        color=WB_COLORS['gray'],
        style='italic'
    )
    
    # Save if path provided
    if save_path:
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    
    return fig, ax


def plot_time_series(
    data: pd.DataFrame,
    date_col: str = 'date',
    value_cols: Optional[List[str]] = None,
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    ylabel: Optional[str] = None,
    xlabel: Optional[str] = None,
    figsize: Tuple[float, float] = (14, 6),
    colors: Optional[List[str]] = None,
    show_zero_line: bool = True,
    save_path: Optional[str] = None,
    dpi: int = 300
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Create a World Bank-styled time series line plot.
    
    Parameters
    ----------
    data : pd.DataFrame
        DataFrame containing time series data
    date_col : str, default 'date'
        Name of the date column
    value_cols : list of str, optional
        List of column names to plot. If None, plots all numeric columns except date_col
    title : str, optional
        Main title for the plot
    subtitle : str, optional
        Subtitle displayed below the title
    ylabel : str, optional
        Y-axis label
    xlabel : str, optional
        X-axis label (default: empty for WB time series style)
    figsize : tuple of float, default (14, 6)
        Figure size (width, height) in inches
    colors : list of str, optional
        List of colors for lines. If None, uses WB categorical palette
    show_zero_line : bool, default True
        Whether to show a horizontal line at y=0
    save_path : str, optional
        Path to save the figure
    dpi : int, default 300
        Resolution for saved figure
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object
    ax : matplotlib.axes.Axes
        The axes object
    """
    # Apply World Bank style
    apply_wb_style()
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    
    # Convert date column to datetime if needed
    if not pd.api.types.is_datetime64_any_dtype(data[date_col]):
        data = data.copy()
        data[date_col] = pd.to_datetime(data[date_col])
    
    # Determine which columns to plot
    if value_cols is None:
        value_cols = [col for col in data.columns if col != date_col and pd.api.types.is_numeric_dtype(data[col])]
    
    # Set up colors
    if colors is None:
        colors = [WB_COLORS['cat1'], WB_COLORS['cat2'], WB_COLORS['cat3'], 
                 WB_COLORS['cat4'], WB_COLORS['cat5'], WB_COLORS['cat6'],
                 WB_COLORS['cat7'], WB_COLORS['cat8'], WB_COLORS['cat9']]
    
    # Plot each value column
    for i, col in enumerate(value_cols):
        ax.plot(
            data[date_col],
            data[col],
            label=col.replace('_', ' ').title(),
            color=colors[i % len(colors)],
            linewidth=2.0
        )
    
    # WB style: set y-axis to start at 0 for timeseries
    ax.set_ylim(bottom=0)
    
    # Add zero line if data crosses zero
    if show_zero_line and data[value_cols].min().min() < 0:
        ax.axhline(y=0, color='#8A969F', linewidth=1, zorder=1)
    
    # Remove x-axis label (WB timeseries style)
    ax.set_xlabel('')
    
    # Y-axis label
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=14, fontweight='semibold', color=WB_COLORS['text'])
    
    # Axes styling
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    
    # Grid styling - only horizontal lines for timeseries
    ax.grid(True, axis='y', linestyle=(0, (4, 2)), linewidth=0.85, color=WB_COLORS['grid'], zorder=0)
    ax.grid(False, axis='x')
    
    # Tick parameters - remove tick marks but keep labels
    ax.tick_params(axis='y', which='both', length=0, labelsize=14, colors=WB_COLORS['text_subtle'])
    ax.tick_params(axis='x', which='both', length=0, labelsize=14, colors=WB_COLORS['text_subtle'])
    
    # Tick label colors
    for label in ax.get_xticklabels():
        label.set_color(WB_COLORS['text_subtle'])
        label.set_fontweight('regular')
    for label in ax.get_yticklabels():
        label.set_color(WB_COLORS['text_subtle'])
        label.set_fontweight('regular')
    
    # Legend - WB style below plot
    if len(value_cols) > 1:
        ax.legend(
            loc='upper left',
            frameon=False,
            fontsize=12
        )
    
    # Title styling (use fig.text for better control)
    if title or subtitle:
        # Calculate positions
        title_y = 0.98
        if title:
            fig.text(
                0.1, title_y,
                title,
                fontsize=20,
                fontweight='bold',
                color=WB_COLORS['text'],
                ha='left',
                va='top'
            )
            title_y -= 0.05
        
        if subtitle:
            fig.text(
                0.1, title_y,
                subtitle,
                fontsize=14,
                color=WB_COLORS['text_subtle'],
                ha='left',
                va='top'
            )
    
    plt.tight_layout()
    
    # Save if path provided
    if save_path:
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    
    return fig, ax


def plot_crop_area_change(
    data: pd.DataFrame,
    boundary_gdf: gpd.GeoDataFrame,
    join_column: str = 'ADM3_EN',
    change_column: str = 'pct_change_2015_2025',
    figsize: Tuple[float, float] = (12, 8),
    title: str = 'Crop Area Change (2015-2025)',
    cmap: str = 'RdYlGn',
    save_path: Optional[str] = None,
    dpi: int = 300
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Create a map showing crop area changes.
    
    Parameters
    ----------
    data : pd.DataFrame
        DataFrame containing crop area data
    boundary_gdf : gpd.GeoDataFrame
        GeoDataFrame with administrative boundaries
    join_column : str, default 'ADM3_EN'
        Column name to join data and boundaries
    change_column : str, default 'pct_change_2015_2025'
        Column name containing change percentage
    figsize : tuple of float, default (12, 8)
        Figure size (width, height) in inches
    title : str
        Title for the map
    cmap : str, default 'RdYlGn'
        Matplotlib colormap name
    save_path : str, optional
        Path to save the figure
    dpi : int, default 300
        Resolution for saved figure
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object
    ax : matplotlib.axes.Axes
        The axes object
    """
    # Merge data with boundaries
    plot_data = boundary_gdf.merge(data[[join_column, change_column]], on=join_column, how='left')
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    
    # Plot
    plot_data.plot(
        column=change_column,
        cmap=cmap,
        ax=ax,
        edgecolor='white',
        linewidth=0.2,
        legend=True,
        legend_kwds={
            'label': 'Percentage Change (%)',
            'orientation': 'horizontal',
            'shrink': 0.8,
            'pad': 0.05,
            'aspect': 30
        },
        missing_kwds={'color': 'lightgrey', 'label': 'No Data'}
    )
    
    ax.set_title(
        title,
        fontsize=16,
        fontweight='bold',
        pad=20,
        color=WB_COLORS['dark_blue']
    )
    ax.axis('off')
    
    plt.tight_layout()
    
    # Save if path provided
    if save_path:
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    
    return fig, ax


def create_time_series_comparison(
    data: pd.DataFrame,
    x_col: str,
    y_cols: List[str],
    group_col: Optional[str] = None,
    title: str = 'Time Series Comparison',
    xlabel: str = 'Date',
    ylabel: str = 'Value',
    figsize: Tuple[float, float] = (14, 6),
    colors: Optional[List[str]] = None,
    save_path: Optional[str] = None,
    dpi: int = 300
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Create time series comparison plots.
    
    Parameters
    ----------
    data : pd.DataFrame
        DataFrame containing time series data
    x_col : str
        Column name for x-axis (typically date/time)
    y_cols : list of str
        Column names to plot on y-axis
    group_col : str, optional
        Column name for grouping (e.g., regions)
    title : str
        Plot title
    xlabel : str
        X-axis label
    ylabel : str
        Y-axis label
    figsize : tuple of float
        Figure size (width, height) in inches
    colors : list of str, optional
        List of colors for lines
    save_path : str, optional
        Path to save the figure
    dpi : int, default 300
        Resolution for saved figure
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object
    ax : matplotlib.axes.Axes
        The axes object
    """
    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    
    if colors is None:
        colors = [WB_COLORS['blue'], WB_COLORS['red'], WB_COLORS['green'], 
                 WB_COLORS['orange'], WB_COLORS['purple']]
    
    if group_col:
        groups = data[group_col].unique()
        for i, group in enumerate(groups):
            group_data = data[data[group_col] == group]
            for j, y_col in enumerate(y_cols):
                ax.plot(
                    group_data[x_col],
                    group_data[y_col],
                    label=f"{group} - {y_col}",
                    color=colors[(i * len(y_cols) + j) % len(colors)],
                    linewidth=2,
                    alpha=0.8
                )
    else:
        for i, y_col in enumerate(y_cols):
            ax.plot(
                data[x_col],
                data[y_col],
                label=y_col,
                color=colors[i % len(colors)],
                linewidth=2,
                alpha=0.8
            )
    
    ax.set_xlabel(xlabel, fontsize=12, color=WB_COLORS['dark_blue'])
    ax.set_ylabel(ylabel, fontsize=12, color=WB_COLORS['dark_blue'])
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20, color=WB_COLORS['dark_blue'])
    ax.legend(loc='best', frameon=True, fancybox=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    
    return fig, ax
