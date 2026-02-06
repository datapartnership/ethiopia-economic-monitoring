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


def plot_parallel_trends_annual(df, treatment_year=2019, title_suffix='', 
                                 figsize=(8, 4), save_path=None, dpi=300, 
                                 print_slopes=True):
    """
    Create annual trends plot for parallel trends assumption in DiD analysis.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing columns: 'year', 'NewConflict' (0=control, 1=treatment), 'EVI'
    treatment_year : int, optional
        Year when treatment starts (default: 2019)
    title_suffix : str, optional
        Additional text to add to plot title (default: '')
    figsize : tuple, optional
        Figure size (default: (8, 4))
    save_path : str, optional
        If provided, saves the figure to this path (default: None)
    dpi : int, optional
        Resolution for saved figure (default: 300)
    print_slopes : bool, optional
        If True, prints slope analysis for pre/post treatment periods (default: True)
    
    Returns:
    --------
    fig, ax : matplotlib figure and axes objects
    slopes : dict
        Dictionary containing slope information for both groups in both periods
    slopes_df : pd.DataFrame
        Formatted table with slope analysis results
    
    Example:
    --------
    >>> fig, ax, slopes, df = plot_parallel_trends_annual(merged, treatment_year=2019, 
    ...                                                     title_suffix='(All Regions)')
    >>> display(df)  # Show formatted table in notebook
    """
    import seaborn as sns
    from scipy import stats
    
    # Calculate annual trends using NewConflict (0=control, 1=treatment)
    annual_trends = df.groupby(['NewConflict', 'year'])['EVI'].median().reset_index()
    
    # Calculate slopes for pre and post treatment periods
    slopes_dict = {}
    
    for new_conflict_val in [0, 1]:  # 0=control, 1=treatment
        cat_data = annual_trends[annual_trends['NewConflict'] == new_conflict_val]
        
        # Pre-treatment period
        pre_data = cat_data[cat_data['year'] < treatment_year]
        if len(pre_data) > 1:
            slope_pre, intercept_pre, r_value_pre, p_value_pre, std_err_pre = \
                stats.linregress(pre_data['year'], pre_data['EVI'])
        else:
            slope_pre, r_value_pre = None, None
        
        # Post-treatment period
        post_data = cat_data[cat_data['year'] >= treatment_year]
        if len(post_data) > 1:
            slope_post, intercept_post, r_value_post, p_value_post, std_err_post = \
                stats.linregress(post_data['year'], post_data['EVI'])
        else:
            slope_post, r_value_post = None, None
        
        slopes_dict[new_conflict_val] = {
            'pre_slope': slope_pre,
            'pre_r2': r_value_pre**2 if r_value_pre else None,
            'post_slope': slope_post,
            'post_r2': r_value_post**2 if r_value_post else None
        }
    
    # Create DataFrame for results
    slope_rows = []
    
    for new_conflict_val in [0, 1]:  # 0=control, 1=treatment
        group_type = 'Control' if new_conflict_val == 0 else 'Treatment'
        
        pre_slope = slopes_dict[new_conflict_val]['pre_slope']
        pre_r2 = slopes_dict[new_conflict_val]['pre_r2']
        post_slope = slopes_dict[new_conflict_val]['post_slope']
        post_r2 = slopes_dict[new_conflict_val]['post_r2']
        
        # Calculate change in slope
        if pre_slope is not None and post_slope is not None:
            slope_change = post_slope - pre_slope
        else:
            slope_change = None
        
        slope_rows.append({
            'Group': group_type,
            f'Pre-{treatment_year}\nSlope (EVI/year)': f"{pre_slope:+.6f}" if pre_slope else "N/A",
            f'Pre-{treatment_year}\nR²': f"{pre_r2:.4f}" if pre_r2 else "N/A",
            f'Post-{treatment_year}\nSlope (EVI/year)': f"{post_slope:+.6f}" if post_slope else "N/A",
            f'Post-{treatment_year}\nR²': f"{post_r2:.4f}" if post_r2 else "N/A",
            'Change in Slope\n(EVI/year)': f"{slope_change:+.6f}" if slope_change else "N/A"
        })
    
    slopes_df = pd.DataFrame(slope_rows)
    
    # Add parallel trends comparison
    control_pre = slopes_dict.get(0, {}).get('pre_slope')
    treatment_pre = slopes_dict.get(1, {}).get('pre_slope')
    
    if control_pre is not None and treatment_pre is not None:
        slope_diff = abs(treatment_pre - control_pre)
        
        if slope_diff < 0.001:
            assessment = "✓ Very similar - strong parallel trends"
        elif slope_diff < 0.005:
            assessment = "✓ Reasonably similar - parallel trends supported"
        else:
            assessment = "⚠ Slopes differ - parallel trends may be violated"
        
        # Add summary row
        summary_row = pd.DataFrame([{
            'Group': 'Pre-Treatment Difference',
            f'Pre-{treatment_year}\nSlope (EVI/year)': f"{slope_diff:.6f}",
            f'Pre-{treatment_year}\nR²': "",
            f'Post-{treatment_year}\nSlope (EVI/year)': "",
            f'Post-{treatment_year}\nR²': "",
            'Change in Slope\n(EVI/year)': assessment
        }])
        slopes_df = pd.concat([slopes_df, summary_row], ignore_index=True)
    
    # Print slope analysis
    if print_slopes:
        print(f"\n{'='*70}")
        print(f"SLOPE ANALYSIS: Rate of Change in EVI (Treatment Year: {treatment_year})")
        print(f"{'='*70}\n")
        print(slopes_df.to_string(index=False))
        print(f"\n{'='*70}\n")
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot annual trends using NewConflict (0=control, 1=treatment)
    for new_conflict_val, color, marker, label in [(0, '#2E86AB', 'o', 'Control'), 
                                                     (1, '#A23B72', 's', 'Treatment')]:
        data = annual_trends[annual_trends['NewConflict'] == new_conflict_val]
        ax.plot(data['year'], data['EVI'], 
                marker=marker, linewidth=1.5, markersize=5, 
                label=label, color=color)
    
    # Add treatment start line
    ax.axvline(x=treatment_year, color='red', linestyle='--', linewidth=1.5, 
               label=f'Treatment Start ({treatment_year})', alpha=0.7)
    
    # Add slope annotations on the plot
    y_min, y_max = ax.get_ylim()
    text_y_pos = y_max - (y_max - y_min) * 0.05  # Start at 95% of plot height
    
    # Control slopes (top)
    control_pre = slopes_dict.get(0, {}).get('pre_slope')
    control_post = slopes_dict.get(0, {}).get('post_slope')
    if control_pre is not None and control_post is not None:
        control_text = f'Control: Pre={control_pre:+.4f}, Post={control_post:+.4f}'
        ax.text(0.02, 0.98, control_text, transform=ax.transAxes,
                fontsize=7, verticalalignment='top', 
                bbox=dict(boxstyle='round', facecolor='#2E86AB', alpha=0.15, edgecolor='#2E86AB'))
    
    # Treatment slopes (below control)
    treatment_pre = slopes_dict.get(1, {}).get('pre_slope')
    treatment_post = slopes_dict.get(1, {}).get('post_slope')
    if treatment_pre is not None and treatment_post is not None:
        treatment_text = f'Treatment: Pre={treatment_pre:+.4f}, Post={treatment_post:+.4f}'
        ax.text(0.02, 0.90, treatment_text, transform=ax.transAxes,
                fontsize=7, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='#A23B72', alpha=0.15, edgecolor='#A23B72'))
    
    # Styling - smaller fonts
    ax.set_xlabel('Year', fontsize=9, fontweight='bold')
    ax.set_ylabel('Median EVI', fontsize=9, fontweight='bold')
    
    title = f'Parallel Trends: EVI Before and After {treatment_year}'
    if title_suffix:
        title += f' {title_suffix}'
    ax.set_title(title, fontsize=10, fontweight='bold')
    ax.legend(fontsize=8, loc='best', framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=8)
    
    plt.tight_layout()
    
    # Save if path provided
    if save_path:
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
        print(f"✓ Saved: {save_path}")
    
    return fig, ax, slopes_dict, slopes_df


def plot_parallel_trends_subplots(model_list, model_names, treatment_year=2019, 
                                   figsize=(15, 4), save_path=None, dpi=300):
    """
    Create subplots with parallel trends plots for multiple models side by side.
    
    Parameters:
    -----------
    model_list : list of pd.DataFrame
        List of DataFrames, each containing data for a model
    model_names : list of str
        List of names/titles for each model
    treatment_year : int, optional
        Year when treatment starts (default: 2019)
    figsize : tuple, optional
        Figure size as (width, height) (default: (15, 4))
    save_path : str, optional
        Path to save the figure (default: None)
    dpi : int, optional
        Resolution for saved figure (default: 300)
    
    Returns:
    --------
    fig : matplotlib.figure.Figure
        The figure object
    axes : array of matplotlib.axes.Axes
        Array of subplot axes
    all_slopes : list of dict
        List of slope dictionaries for each model
    all_slopes_df : list of pd.DataFrame
        List of slopes DataFrames for each model
    """
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    from scipy.stats import linregress
    
    n_models = len(model_list)
    fig, axes = plt.subplots(1, n_models, figsize=figsize)
    
    # Ensure axes is always an array
    if n_models == 1:
        axes = [axes]
    
    all_slopes = []
    all_slopes_df = []
    
    for idx, (model_df, model_name) in enumerate(zip(model_list, model_names)):
        ax = axes[idx]
        
        # Prepare data
        df = model_df.copy()
        df['year'] = df['date'].dt.year
        
        # Annual aggregation
        df_annual = df.groupby(['admin_category', 'year'])['EVI'].median().reset_index()
        
        # Calculate slopes
        slopes_dict = {}
        slopes_data = []
        
        for admin_cat in df_annual['admin_category'].unique():
            cat_data = df_annual[df_annual['admin_category'] == admin_cat]
            
            # Pre-treatment slope
            pre_data = cat_data[cat_data['year'] < treatment_year]
            if len(pre_data) >= 2:
                slope_pre, intercept_pre, r_pre, p_pre, se_pre = linregress(
                    pre_data['year'], pre_data['EVI']
                )
                slopes_data.append({
                    'admin_category': admin_cat,
                    'period': 'Pre',
                    'slope': slope_pre,
                    'p_value': p_pre,
                    'r_squared': r_pre**2
                })
            else:
                slope_pre = None
            
            # Post-treatment slope
            post_data = cat_data[cat_data['year'] >= treatment_year]
            if len(post_data) >= 2:
                slope_post, intercept_post, r_post, p_post, se_post = linregress(
                    post_data['year'], post_data['EVI']
                )
                slopes_data.append({
                    'admin_category': admin_cat,
                    'period': 'Post',
                    'slope': slope_post,
                    'p_value': p_post,
                    'r_squared': r_post**2
                })
            else:
                slope_post = None
            
            # Store in dict
            cat_code = 1 if admin_cat == 'New Conflict' else 0
            slopes_dict[cat_code] = {
                'pre_slope': slope_pre,
                'post_slope': slope_post,
                'admin_category': admin_cat
            }
        
        slopes_df = pd.DataFrame(slopes_data)
        all_slopes.append(slopes_dict)
        all_slopes_df.append(slopes_df)
        
        # Plot lines
        for admin_cat in df_annual['admin_category'].unique():
            cat_data = df_annual[df_annual['admin_category'] == admin_cat]
            
            # Assign colors based on admin category
            if 'No' in admin_cat or 'Low' in admin_cat or 'Control' in admin_cat:
                color = '#2E86AB'  # Blue for control
            else:
                color = '#A23B72'  # Purple/red for treatment
            label = admin_cat
            
            ax.plot(cat_data['year'], cat_data['EVI'], 
                   marker='o', linewidth=2, label=label, color=color, markersize=4)
        
        # Add vertical line at treatment year
        ax.axvline(x=treatment_year, color='red', linestyle='--', 
                  linewidth=1.5, alpha=0.7, label=f'Treatment ({treatment_year})')
        
        # Add slope annotations
        control_pre = slopes_dict.get(0, {}).get('pre_slope')
        control_post = slopes_dict.get(0, {}).get('post_slope')
        if control_pre is not None and control_post is not None:
            control_text = f'Control: Pre={control_pre:+.4f}, Post={control_post:+.4f}'
            ax.text(0.02, 0.98, control_text, transform=ax.transAxes,
                   fontsize=7, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='#2E86AB', alpha=0.15, edgecolor='#2E86AB'))
        
        treatment_pre = slopes_dict.get(1, {}).get('pre_slope')
        treatment_post = slopes_dict.get(1, {}).get('post_slope')
        if treatment_pre is not None and treatment_post is not None:
            treatment_text = f'Treatment: Pre={treatment_pre:+.4f}, Post={treatment_post:+.4f}'
            ax.text(0.02, 0.90, treatment_text, transform=ax.transAxes,
                   fontsize=7, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='#A23B72', alpha=0.15, edgecolor='#A23B72'))
        
        # Styling
        ax.set_xlabel('Year', fontsize=9, fontweight='bold')
        ax.set_ylabel('Median EVI', fontsize=9, fontweight='bold')
        ax.set_title(model_name, fontsize=10, fontweight='bold')
        ax.legend(fontsize=7, loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3)
        ax.tick_params(labelsize=8)
    
    plt.tight_layout()
    
    # Save if path provided
    if save_path:
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
        print(f"✓ Saved: {save_path}")
    
    return fig, axes, all_slopes, all_slopes_df


def plot_evi_distribution_by_period(df, treatment_year=2019, title_suffix='',
                                    figsize=(7, 4), save_path=None, dpi=300):
    """
    Create boxplot showing EVI distribution by period and treatment group.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing columns: 'EVI', 'NewConflict', 'Post_t'
    treatment_year : int, optional
        Year when treatment starts (default: 2019)
    title_suffix : str, optional
        Additional text to add to plot title (default: '')
    figsize : tuple, optional
        Figure size (default: (7, 4))
    save_path : str, optional
        If provided, saves the figure to this path (default: None)
    dpi : int, optional
        Resolution for saved figure (default: 300)
    
    Returns:
    --------
    fig, ax : matplotlib figure and axes objects
    
    Example:
    --------
    >>> fig, ax = plot_evi_distribution_by_period(model1, treatment_year=2019,
    ...                                            title_suffix='(Matched Sample)')
    """
    import seaborn as sns
    
    # Prepare data
    data_plot = df.copy()
    data_plot['Period'] = data_plot['Post_t'].map({0: f'Pre-{treatment_year}', 
                                                     1: f'Post-{treatment_year}'})
    data_plot['Group'] = data_plot['NewConflict'].map({0: 'Control', 1: 'Treatment'})
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create boxplot
    sns.boxplot(data=data_plot, x='Period', y='EVI', hue='Group', 
                ax=ax, palette=['#2E86AB', '#A23B72'])
    
    # Styling - smaller fonts
    title = 'EVI Distribution by Period and Group'
    if title_suffix:
        title += f' {title_suffix}'
    ax.set_title(title, fontsize=10, fontweight='bold')
    ax.set_xlabel('Period', fontsize=9, fontweight='bold')
    ax.set_ylabel('EVI', fontsize=9, fontweight='bold')
    ax.legend(fontsize=8, loc='best', framealpha=0.9)
    ax.grid(True, alpha=0.3, axis='y')
    ax.tick_params(labelsize=8)
    
    plt.tight_layout()
    
    # Save if path provided
    if save_path:
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
        print(f"✓ Saved: {save_path}")
    
    return fig, ax


def plot_crop_area_quartiles(crop_area_adm3_tot, eth_adm3, eth_adm1, 
                              ax=None, figsize=(7, 6), save_path=None, dpi=300):
    """
    Create a map showing crop area distribution by ADM3 region in quartiles.
    
    Parameters:
    -----------
    crop_area_adm3_tot : pd.DataFrame
        DataFrame with columns: 'ADM3_EN', 'crop_area' (aggregated crop area by region)
    eth_adm3 : gpd.GeoDataFrame
        GeoDataFrame with ADM3 boundaries containing 'ADM3_EN' and 'geometry'
    eth_adm1 : gpd.GeoDataFrame
        GeoDataFrame with ADM1 boundaries for reference lines
    ax : matplotlib.axes.Axes, optional
        If provided, plot on this axis (for subplots). Otherwise creates new figure.
    figsize : tuple, optional
        Figure size (default: (7, 6)). Only used if ax is None.
    save_path : str, optional
        If provided, saves the figure to this path (default: None)
    dpi : int, optional
        Resolution for saved figure (default: 300)
    
    Returns:
    --------
    fig, ax : matplotlib figure and axes objects
    crop_area_map : gpd.GeoDataFrame
        GeoDataFrame with quartile assignments for further analysis
    
    Example:
    --------
    >>> crop_area_adm3_tot = crop_area_adm3.groupby(['ADM3_EN'])['crop_area'].mean().reset_index()
    >>> fig, ax, crop_map = plot_crop_area_quartiles(crop_area_adm3_tot, eth_adm3, eth_adm1)
    """
    # Create copy to avoid modifying original
    crop_area_df = crop_area_adm3_tot.copy()
    
    # Assign quartiles to all regions
    crop_area_df['quartile'] = pd.qcut(crop_area_df['crop_area'], 
                                        q=4, 
                                        labels=['Q1 (Bottom 25%)', 'Q2', 'Q3', 'Q4 (Top 25%)'])
    
    # Calculate area for each quartile
    quartile_stats = []
    for quartile in ['Q1 (Bottom 25%)', 'Q2', 'Q3', 'Q4 (Top 25%)']:
        q_data = crop_area_df[crop_area_df['quartile'] == quartile]
        mean_area = q_data['crop_area'].mean()
        quartile_stats.append(f"{quartile}\n({mean_area:.0f} ha avg)")
    
    # Merge with geometry
    crop_area_map = eth_adm3[['ADM3_EN', 'geometry']].merge(crop_area_df, on='ADM3_EN', how='left')
    
    # Create custom labels with area info
    crop_area_map['quartile_label'] = crop_area_map['quartile'].map({
        'Q1 (Bottom 25%)': quartile_stats[0],
        'Q2': quartile_stats[1],
        'Q3': quartile_stats[2],
        'Q4 (Top 25%)': quartile_stats[3]
    })
    
    # Create the map - conditionally create new figure or use provided axis
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize)
    else:
        fig = ax.get_figure()
    
    # Plot the quartiles
    crop_area_map.plot(column='quartile_label', 
                        ax=ax,
                        legend=True,
                        categorical=True,
                        cmap='YlGn',
                        edgecolor='black',
                        linewidth=0.3,
                        legend_kwds={'loc': 'lower left', 'fontsize': 7})
    
    # Add ADM1 boundaries for reference
    eth_adm1.boundary.plot(ax=ax, color='black', linewidth=1.5, alpha=0.8)
    
    # Styling
    ax.set_title('Crop Area Distribution by ADM3 Region\nQuartile Classification', 
                 fontsize=10, fontweight='bold', pad=20)
    ax.axis('off')
    
    # Only call tight_layout and show if we created the figure
    if save_path or ax is None:
        plt.tight_layout()
    
    # Save if path provided
    if save_path:
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
        print(f"✓ Saved: {save_path}")
    
    # Only show if we created a standalone figure
    if ax is None:
        plt.show()
    
    return fig, ax, crop_area_map


def plot_conflict_categories_map(eth_adm3, eth_adm1, bottom_half_regions_set, 
                                  no_conflict, low_conflict_list, new_conflict, 
                                  reduced_conflict, persistent_conflict,
                                  figsize=(7, 6), save_path=None, dpi=300):
    """
    Create a map showing conflict categories by ADM3 region.
    
    Parameters:
    -----------
    eth_adm3 : gpd.GeoDataFrame
        GeoDataFrame with ADM3 boundaries containing 'ADM3_EN' and 'geometry'
    eth_adm1 : gpd.GeoDataFrame
        GeoDataFrame with ADM1 boundaries for reference lines
    bottom_half_regions_set : set
        Set of ADM3 region names in bottom quartile (excluded from analysis)
    no_conflict : list
        List of ADM3 region names with no conflict
    low_conflict_list : list
        List of ADM3 region names with low conflict (<=10 events per period)
    new_conflict : list
        List of ADM3 region names with new conflict (pre<=10, post>10)
    reduced_conflict : list
        List of ADM3 region names with reduced conflict (pre>10, post<=10)
    persistent_conflict : list
        List of ADM3 region names with persistent conflict (>10 both periods)
    figsize : tuple, optional
        Figure size (default: (7, 6))
    save_path : str, optional
        If provided, saves the figure to this path (default: None)
    dpi : int, optional
        Resolution for saved figure (default: 300)
    
    Returns:
    --------
    fig, ax : matplotlib figure and axes objects
    conflict_map : gpd.GeoDataFrame
        GeoDataFrame with conflict category assignments
    
    Example:
    --------
    >>> fig, ax, conflict_map = plot_conflict_categories_map(
    ...     eth_adm3, eth_adm1, bottom_half_regions_set,
    ...     no_conflict, low_conflict_list, new_conflict,
    ...     reduced_conflict, persistent_conflict
    ... )
    """
    from matplotlib.patches import Patch
    
    # Create a dataframe mapping regions to conflict categories
    conflict_categories = []

    for adm3 in eth_adm3['ADM3_EN'].unique():
        if adm3 in bottom_half_regions_set:
            category = 'Excluded (Low Crop Area)'
        elif adm3 in no_conflict:
            category = 'No Conflict'
        elif adm3 in low_conflict_list:
            category = 'Low Conflict'
        elif adm3 in new_conflict:
            category = 'New Conflict'
        elif adm3 in reduced_conflict:
            category = 'Reduced Conflict'
        elif adm3 in persistent_conflict:
            category = 'Persistent Conflict'
        else:
            category = 'Uncategorized'
        
        conflict_categories.append({'ADM3_EN': adm3, 'conflict_category': category})

    conflict_cat_df = pd.DataFrame(conflict_categories)

    # Merge with geometry
    conflict_map = eth_adm3[['ADM3_EN', 'geometry']].merge(conflict_cat_df, on='ADM3_EN', how='left')

    # Define custom colors using WB palette
    category_colors = {
        'Excluded (Low Crop Area)': '#CED4DE',  # WB grid color
        'No Conflict': '#00AB51',  # WB green
        'Low Conflict':'blue',  # WB cat1 blue
        'New Conflict': '#EB1C2D',  # WB red
        'Reduced Conflict': '#FF9800',  # WB cat2 orange
        'Persistent Conflict': '#664AB6'  # WB cat3 purple
    }

    # Create the map
    fig, ax = plt.subplots(1, 1, figsize=figsize)

    # Plot using the column with categorical coloring
    conflict_map['color'] = conflict_map['conflict_category'].map(category_colors)
    conflict_map.plot(ax=ax, color=conflict_map['color'], edgecolor='black', linewidth=0.2)

    # Add ADM1 boundaries
    eth_adm1.boundary.plot(ax=ax, color='black', linewidth=1.5, alpha=0.8)

    # Create legend manually
    legend_elements = [Patch(facecolor=color, edgecolor='none', label=category) 
                       for category, color in category_colors.items()]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=7, 
              title='Conflict Category', title_fontsize=8, framealpha=0.9)

    # Styling
    ax.set_title('Conflict Categories by ADM3 Region\n(Excluding Bottom Quartile Crop Area)', 
                 fontsize=10, fontweight='bold', pad=20)
    ax.axis('off')

    plt.tight_layout()
    
    # Save if path provided
    if save_path:
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
        print(f"✓ Saved: {save_path}")
    
    plt.show()

    # Print summary
    for category in category_colors.keys():
        count = len(conflict_map[conflict_map['conflict_category'] == category])
        print(f"{category}: {count} regions")

    return fig, ax, conflict_map


def plot_lst_by_year(region_lists, titles=None, start_year=2012, metric='lst_mean', figsize=None, lst_data=None):
    """
    Plot LST trends with each year as a separate line for multiple region groups.
    
    Parameters:
    -----------
    region_lists : list of lists
        Each inner list contains ADM3 region names to filter and plot
    titles : list of str, optional
        Titles for each subplot. If None, will use "Group 1", "Group 2", etc.
    start_year : int, default 2012
        Starting year to include in the plot
    metric : str, default 'lst_mean'
        LST metric to plot ('lst_mean' or 'lst_max')
    figsize : tuple, optional
        Figure size (width, height). If None, auto-calculated based on number of plots
    lst_data : pd.DataFrame, optional
        LST dataframe with columns ['ADM3_EN', 'date', 'lst_mean', 'lst_max'].
        If None, will look for 'lst' in global scope (for backward compatibility)
    
    Returns:
    --------
    fig, axes : matplotlib figure and axes objects
    
    Example:
    --------
    >>> plot_lst_by_year([no_conflict_tigray, new_conflict_tigray], 
    ...                   titles=['No Conflict Regions', 'New Conflict Regions'],
    ...                   start_year=2020)
    """
    # Handle lst data parameter
    if lst_data is None:
        import inspect
        frame = inspect.currentframe().f_back
        if 'lst' in frame.f_locals:
            lst = frame.f_locals['lst']
        elif 'lst' in frame.f_globals:
            lst = frame.f_globals['lst']
        else:
            raise ValueError("lst_data parameter is required or 'lst' must be available in calling scope")
    else:
        lst = lst_data
    
    n_plots = len(region_lists)
    
    # Auto-generate titles if not provided
    if titles is None:
        titles = [f'Region Group {i+1}' for i in range(n_plots)]
    
    # Auto-calculate figure size if not provided
    if figsize is None:
        figsize = (6 * n_plots, 4) if n_plots <= 2 else (4 * n_plots, 6)
    
    # Create subplots
    fig, axes = plt.subplots(1, n_plots, figsize=figsize, sharey=True)
    
    # Handle single subplot case (axes won't be array)
    if n_plots == 1:
        axes = [axes]
    
    # Plot each region group
    for idx, (regions, title) in enumerate(zip(region_lists, titles)):
        ax = axes[idx]
        
        # Filter data for this region group
        lst_filtered = lst[lst['ADM3_EN'].isin(regions)].copy()
        lst_filtered['month'] = lst_filtered['date'].dt.month
        lst_filtered['year'] = lst_filtered['date'].dt.year
        lst_filtered = lst_filtered[lst_filtered['year'] >= start_year]
        
        # Calculate monthly averages by year
        lst_monthly = lst_filtered.groupby(['year', 'month'])[[metric, 'lst_max']].mean().reset_index()
        
        # Plot each year as a separate line
        for year in sorted(lst_monthly['year'].unique()):
            year_data = lst_monthly[lst_monthly['year'] == year]
            ax.plot(year_data['month'], year_data[metric], label=str(year), linewidth=2)
        
        # Formatting
        ax.set_xlabel('Month', fontsize=11, fontweight='bold')
        ylabel = 'Mean LST (°C)' if metric == 'lst_mean' else 'Max LST (°C)'
        ax.set_ylabel(ylabel, fontsize=11, fontweight='bold')
        ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], fontsize=9)
        ax.legend(title='Year', bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3)
        
        # Add region count to title
        n_regions = len(regions)
        ax.text(0.02, 0.98, f'n={n_regions} regions', transform=ax.transAxes,
                fontsize=8, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
    
    plt.tight_layout()
    return fig, axes


def plot_crop_season_patterns(eth_adm3, crop_season, eth_adm1=None, figsize=(12, 10), 
                               ax=None, return_map=False):
    """
    Plot crop season patterns by ADM3 region.
    
    Creates a choropleth map showing different crop season patterns based on 
    start of season (SOS) and end of season (EOS) data. Regions with similar 
    patterns are grouped together with distinct colors.
    
    Parameters
    ----------
    eth_adm3 : GeoDataFrame
        Administrative level 3 boundaries with 'ADM3_EN' and 'geometry' columns
    crop_season : DataFrame
        Crop season data with columns: 'Name', 'sos' (start of season), 
        'eos' (end of season). Optional: 'mos' (middle of season)
    eth_adm1 : GeoDataFrame, optional
        Administrative level 1 boundaries to overlay on the map
    figsize : tuple, default (12, 10)
        Figure size (width, height) in inches
    ax : matplotlib.axes.Axes, optional
        Existing axes to plot on. If None, creates new figure and axes
    return_map : bool, default False
        Whether to return the merged crop season map GeoDataFrame
        
    Returns
    -------
    fig : matplotlib.figure.Figure or None
        Figure object (None if ax was provided)
    ax : matplotlib.axes.Axes
        Axes object with the plot
    crop_season_map : GeoDataFrame, optional
        Merged geodataframe with season patterns (only if return_map=True)
        
    Examples
    --------
    >>> fig, ax = plot_crop_season_patterns(eth_adm3, crop_season, eth_adm1)
    >>> plt.show()
    
    >>> # Use existing axes
    >>> fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    >>> _, ax, crop_map = plot_crop_season_patterns(
    ...     eth_adm3, crop_season, ax=ax, return_map=True
    ... )
    """
    import matplotlib.cm as cm
    from matplotlib.patches import Patch
    
    # Create figure if ax not provided
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize)
    else:
        fig = None
    
    # Merge crop season data with eth_adm3 geodataframe
    crop_season_map = eth_adm3[['ADM3_EN', 'geometry']].merge(
        crop_season, 
        left_on='ADM3_EN', 
        right_on='Name', 
        how='left'
    )
    
    # Create a unique identifier for each crop season pattern
    # Combine sos (start of season) and eos (end of season)
    crop_season_map['season_pattern'] = crop_season_map.apply(
        lambda row: f"SOS:{int(row['sos'])} EOS:{int(row['eos'])}" 
        if pd.notna(row['sos']) and pd.notna(row['eos']) 
        else 'No Data', 
        axis=1
    )
    
    # Get unique season patterns
    unique_patterns = crop_season_map[crop_season_map['season_pattern'] != 'No Data']['season_pattern'].unique()
    
    # Print statistics
    print(f"Number of unique crop season patterns: {len(unique_patterns)}")
    pattern_counts = crop_season_map['season_pattern'].value_counts()
    regions_with_data = pattern_counts.sum() - pattern_counts.get('No Data', 0)
    regions_without_data = pattern_counts.get('No Data', 0)
    print(f"Regions with crop season data: {regions_with_data}")
    print(f"Regions without data: {regions_without_data}")
    
    # Create categorical color mapping
    n_patterns = len(unique_patterns)
    
    if n_patterns > 0:
        # Generate distinct colors for each pattern
        colors = cm.tab20(np.linspace(0, 1, min(n_patterns, 20)))
        pattern_colors = {pattern: colors[i % 20] for i, pattern in enumerate(unique_patterns)}
        pattern_colors['No Data'] = '#CCCCCC'  # Gray for missing data
        
        crop_season_map['color'] = crop_season_map['season_pattern'].map(pattern_colors)
        
        # Plot the map
        crop_season_map.plot(ax=ax, color=crop_season_map['color'], 
                            edgecolor='black', linewidth=0.3)
        
        # Add ADM1 boundaries if provided
        if eth_adm1 is not None:
            eth_adm1.boundary.plot(ax=ax, color='black', linewidth=1.5, alpha=0.8)
        
        # Create legend (showing top patterns if too many)
        # Show top 10 patterns plus "No Data"
        top_patterns = pattern_counts[pattern_counts.index != 'No Data'].head(10).index.tolist()
        if 'No Data' in pattern_counts:
            top_patterns.append('No Data')
        
        legend_elements = [
            Patch(facecolor=pattern_colors[pattern], edgecolor='black', 
                  label=f"{pattern} (n={pattern_counts[pattern]})")
            for pattern in top_patterns
        ]
        
        ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5), 
                  fontsize=8, title='Crop Season Patterns\n(SOS=Start, EOS=End of Season)', 
                  title_fontsize=9, framealpha=0.95)
        
        ax.set_title('Crop Season Distribution by ADM3 Region', 
                     fontsize=14, fontweight='bold', pad=20)
        ax.axis('off')
        
        # Print pattern statistics
        print("\n=== Top 10 Crop Season Patterns ===")
        for i, (pattern, count) in enumerate(pattern_counts.head(10).items(), 1):
            print(f"{i}. {pattern}: {count} regions")
    else:
        print("No valid crop season data found!")
        ax.text(0.5, 0.5, 'No valid crop season data found', 
                ha='center', va='center', transform=ax.transAxes,
                fontsize=14, fontweight='bold')
        ax.axis('off')
    
    if return_map:
        return fig, ax, crop_season_map
    else:
        return fig, ax


def plot_cluster_assignments_map(cluster_assignments, adm3_geo, adm1_geo=None, 
                                 title='Climate-Based Clusters', figsize=None):
    """
    Visualize cluster assignments on map with separate subplot for each cluster.
    
    Creates a multi-panel map showing cluster assignments with treatment/control
    status overlays. Each cluster gets its own subplot with highlighted regions
    and colored borders indicating conflict status.
    
    Parameters
    ----------
    cluster_assignments : DataFrame
        DataFrame with columns: 'ADM3_EN', 'cluster', 'conflict_status'
        where conflict_status should be 'Treatment' or 'Control'
    adm3_geo : GeoDataFrame
        Administrative level 3 boundaries with 'ADM3_EN' and 'geometry' columns
    adm1_geo : GeoDataFrame, optional
        Administrative level 1 boundaries to overlay on the map
    title : str, default 'Climate-Based Clusters'
        Main title for the figure
    figsize : tuple, optional
        Figure size (width, height). If None, automatically calculated based on number of clusters
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure object with the cluster maps
    axes : array of matplotlib.axes.Axes
        Array of axes objects for each subplot
    map_data : GeoDataFrame
        Merged geodataframe with cluster assignments
        
    Examples
    --------
    >>> fig, axes, map_data = plot_cluster_assignments_map(
    ...     cluster_assignments=cluster_df,
    ...     adm3_geo=eth_adm3,
    ...     adm1_geo=eth_adm1,
    ...     title='Climate Clusters: Tigray War Regions'
    ... )
    >>> plt.show()
    """
    import matplotlib.pyplot as plt
    
    # Merge cluster assignments with geographic data
    map_data_clusters = adm3_geo.merge(
        cluster_assignments[['ADM3_EN', 'cluster', 'conflict_status']], 
        on='ADM3_EN', 
        how='left'
    )
    
    # Get unique clusters (excluding NaN/missing)
    unique_clusters = sorted([c for c in map_data_clusters['cluster'].unique() if pd.notna(c)])
    n_clusters = len(unique_clusters)
    
    # Calculate figure size if not provided
    if figsize is None:
        figsize = (7 * n_clusters, 8)
    
    # Create subplots - one for each cluster
    fig, axes = plt.subplots(1, n_clusters, figsize=figsize)
    
    # Handle case of single cluster
    if n_clusters == 1:
        axes = [axes]
    
    # Plot each cluster in its own subplot
    for idx, cluster_id in enumerate(unique_clusters):
        ax = axes[idx]
        
        # Create a binary column: 1 if in this cluster, 0 otherwise
        map_data_clusters['in_cluster'] = (map_data_clusters['cluster'] == cluster_id).astype(int)
        
        # Plot base map (all regions in light gray)
        adm3_geo.plot(ax=ax, color='lightgray', edgecolor='black', linewidth=0.3, alpha=0.3)
        
        # Highlight regions in this cluster
        cluster_regions = map_data_clusters[map_data_clusters['cluster'] == cluster_id]
        if len(cluster_regions) > 0:
            cluster_regions.plot(ax=ax, color='steelblue', edgecolor='black', linewidth=0.5, alpha=0.6)
        
        # Add conflict status overlays with colored borders
        for status, linewidth, color in [
            ('Treatment', 3.0, 'red'),
            ('Control', 3.0, 'blue')
        ]:
            status_regions = cluster_regions[cluster_regions['conflict_status'] == status]
            if len(status_regions) > 0:
                status_regions.boundary.plot(ax=ax, linewidth=linewidth, color=color, label=status, alpha=0.8)
        
        # Add ADM1 boundaries if provided
        if adm1_geo is not None:
            adm1_geo.boundary.plot(ax=ax, color='black', linewidth=1.5, alpha=0.5)
        
        # Calculate statistics for this cluster
        n_total = len(cluster_regions)
        n_treatment = len(cluster_regions[cluster_regions['conflict_status'] == 'Treatment'])
        n_control = len(cluster_regions[cluster_regions['conflict_status'] == 'Control'])
        
        # Add title with statistics
        ax.set_title(f'Cluster {cluster_id}\n{n_total} regions | Treatment: {n_treatment} | Control: {n_control}', 
                     fontsize=12, fontweight='bold', pad=10)
        ax.axis('off')
        
        # Add legend only to first subplot
        if idx == 0:
            ax.legend(loc='lower left', fontsize=9, framealpha=0.9)
    
    # Add overall title
    fig.suptitle(title, fontsize=14, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    
    # Print cluster summary
    print("\nCluster Map Summary:")
    print("="*80)
    for cluster_id in unique_clusters:
        cluster_data = map_data_clusters[map_data_clusters['cluster'] == cluster_id]
        n_total = len(cluster_data)
        n_treatment = len(cluster_data[cluster_data['conflict_status'] == 'Treatment'])
        n_control = len(cluster_data[cluster_data['conflict_status'] == 'Control'])
        print(f"Cluster {cluster_id}: {n_total} regions ({n_treatment} treatment, {n_control} control)")
    print("\nLegend:")
    print("  - Blue filled = Regions in cluster")
    print("  - Red borders = Treatment regions (new conflict)")
    print("  - Blue borders = Control regions (no/low conflict)")
    
    return fig, axes, map_data_clusters
