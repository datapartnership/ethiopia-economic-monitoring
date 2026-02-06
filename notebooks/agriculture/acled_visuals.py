import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np
from matplotlib.patches import Patch
import pandas as pd
from bokeh.palettes import Category10 # Import a standard color palette
import jenkspy # Import for Jenks natural breaks classification

def create_comparative_maps(data, title, measures=None, aggregation='h3',
                            categories=None, cmaps=None, plot_type='color',
                            boundary_gdf=None, figsize=(15, 5), color_dict=None,
                            layout='columns', binning_method='jenks', n_bins=4): # Added binning parameters
    """
    Creates comparative maps based on specified measures, aggregation levels, and categories.

    Parameters:
    -----------
    data : GeoDataFrame
        The spatial data to plot
    title : str
        The title for the figure
    measures : str, list, or dict
        - If str: single measure to plot
        - If list: multiple measures to plot with different colors
        - If dict: {measure_name: {options}} for advanced configuration
    aggregation : str
        Type of spatial aggregation: 'h3', 'latlon', or 'admin'
    categories : list or None
        List of category values to create separate maps for (e.g., time periods)
        If None, no category separation is applied
    cmaps : str, list, or dict
        Color maps to use for different measures:
        - If str: single colormap for all measures
        - If list: list of colormaps matching measures list
        - If dict: {measure_name: colormap} for specific mapping
    plot_type : str
        'color' for choropleth maps with binned data
        'size' for bubble maps where size indicates value
        'both' for maps with both size and color coding
    boundary_gdf : GeoDataFrame or None
        GeoDataFrame containing boundary lines to plot (e.g., country borders)
    figsize : tuple
        Figure size as (width, height)
    color_dict : dict or None
        User-defined colors for specific measures, e.g., {'nrEvents': 'Blues', 'custom_measure': 'Greens'}
    layout : str, optional
        Determines the layout of subplots: 'columns' for side-by-side, 'rows' for stacked.
        Defaults to 'columns'.
    binning_method : str, optional
        Method used for binning data in choropleth maps. Options are:
        - 'jenks': Jenks natural breaks optimization (default)
        - 'quantile': Equal-sized groups (quartiles)
        - 'equal': Equal interval bins
    n_bins : int, optional
        Number of bins to use for the choropleth maps. Default is 4.

    Returns:
    --------
    fig, ax : matplotlib figure and axes objects
    """
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    from matplotlib.colors import Normalize
    from datetime import datetime
    # import geopandas as gpd # Ensure geopandas is imported if data is GeoDataFrame - assuming it's imported globally or passed correctly

    font_choice = 'Arial'

    # Default values
    if measures is None:
        measures = data.select_dtypes(include=np.number).columns[0]

    # Convert measures to standardized format (always a dictionary)
    if isinstance(measures, str):
        measures = {measures: {}}
    elif isinstance(measures, list):
        measures = {m: {} for m in measures}

    # Set default categories if none provided (single map)
    if categories is None:
        categories = ['All Data']
        if 'category' not in data.columns:
            data['category'] = 'All Data'

    # Set up default colormaps
    default_cmaps = {
        'nrEvents': 'Blues',
        'nrFatalities': 'Reds',
    }

    # Process user-provided color dict (overrides the defaults)
    if color_dict is not None:
        default_cmaps.update(color_dict)

    # Set up measure-specific options
    for measure_name in measures.keys():
        # Set default colormap if not specified
        if 'cmap' not in measures[measure_name]:
            if cmaps is not None:
                if isinstance(cmaps, str):
                    measures[measure_name]['cmap'] = cmaps
                elif isinstance(cmaps, list) and len(cmaps) == len(measures):
                    measures[measure_name]['cmap'] = cmaps[list(measures.keys()).index(measure_name)]
                elif isinstance(cmaps, dict) and measure_name in cmaps:
                    measures[measure_name]['cmap'] = cmaps[measure_name]
                else:
                    measures[measure_name]['cmap'] = default_cmaps.get(measure_name, 'Purples')
            else:
                measures[measure_name]['cmap'] = default_cmaps.get(measure_name, 'Purples')

        # Set default alpha if not specified
        if 'alpha' not in measures[measure_name]:
            measures[measure_name]['alpha'] = 0.7

        # Set default size factor for sizes - adjusted for better scaling
        if 'size_factor' not in measures[measure_name]:
            if plot_type == 'size' or plot_type == 'both':
                measures[measure_name]['size_factor'] = 100
            else:
                measures[measure_name]['size_factor'] = 5

        # Set default label name if not specified
        if 'label_name' not in measures[measure_name]:
            measures[measure_name]['label_name'] = measure_name

    # Determine grid dimensions based on layout
    n_categories = len(categories)
    if layout == 'columns':
        nrows = 1
        ncols = n_categories
    elif layout == 'rows':
        nrows = n_categories
        ncols = 1
    else:
        raise ValueError("Invalid 'layout' parameter. Must be 'columns' or 'rows'.")

    # Create figure and axes with gridspec
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(nrows, ncols, wspace=0.05, hspace=0.05)
    axes = []

    # Create axes with equal size and distribution
    for i in range(n_categories):
        if layout == 'columns':
            ax = fig.add_subplot(gs[0, i])
        else: # layout == 'rows'
            ax = fig.add_subplot(gs[i, 0])
        axes.append(ax)

        # Immediately disable all ticks and spines for each subplot
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        for spine in ax.spines.values():
            spine.set_visible(False)

    # Handle single subplot case (if only one category)
    if n_categories == 1:
        axes = [axes[0]] # Ensure axes is always a list for consistent indexing later

    # Create a deep copy of the dataframe to avoid SettingWithCopyWarning
    plot_data = data.copy(deep=True)

    # Process each measure for binning if using color mapping
    if plot_type in ['color', 'both']:
        for measure_name in measures.keys():
            # Filter out NaN values for calculations
            non_nan_data = plot_data[plot_data[measure_name].notna()]

            if len(non_nan_data) == 0:
                print(f"Warning: No valid data for measure '{measure_name}' for binning calculation.")
                continue

            try:
                # Get min and max values for potential fallback methods
                min_val = non_nan_data[measure_name].min()
                max_val = non_nan_data[measure_name].max()
                
                # Generate bin labels based on n_bins
                bin_labels = [f'B{i+1}' for i in range(n_bins)]
                
                # Default bin edges if calculations fail
                bin_edges = None
                
                # Calculate bins based on the selected method
                if binning_method == 'jenks':
                    # Jenks natural breaks optimization
                    if min_val == max_val:  # Can't do Jenks if all values are the same
                        raise ValueError("All values are identical, can't use Jenks breaks")
                        
                    # Check if we have enough unique values for the requested number of bins
                    unique_values = non_nan_data[measure_name].unique()
                    if len(unique_values) < n_bins + 1:
                        # Not enough unique values, fall back to equal bins
                        print(f"Warning: Not enough unique values for {n_bins} Jenks breaks, using equal interval")
                        bin_edges = np.linspace(min_val, max_val + 1e-9, n_bins + 1).tolist()
                    else:
                        # Calculate Jenks natural breaks
                        breaks = jenkspy.jenks_breaks(non_nan_data[measure_name].values, n_bins + 1)
                        bin_edges = breaks
                        
                        # Ensure last value includes the max
                        if bin_edges[-1] < max_val:
                            bin_edges[-1] = max_val + 1e-9
                
                elif binning_method == 'quantile':
                    # Calculate quantiles for equal-sized groups
                    q_values = np.linspace(0, 1, n_bins + 1).tolist()
                    quantiles = non_nan_data[measure_name].quantile(q_values).tolist()
                    
                    # Handle duplicate values
                    bin_edges = []
                    for q in quantiles:
                        if not bin_edges or q > bin_edges[-1]:
                            bin_edges.append(q)
                    
                    # If we don't have enough unique bin edges
                    if len(bin_edges) < n_bins + 1:
                        missing_bins = n_bins + 1 - len(bin_edges)
                        if min_val == max_val:  # All values are identical
                            epsilon = 1e-10 * max(1, abs(min_val))
                            bin_edges = [min_val - epsilon]
                            for i in range(n_bins):
                                bin_edges.append(min_val + i * epsilon)
                        else:
                            # Create evenly spaced bins to fill the gaps
                            temp_bins = np.linspace(min_val, max_val, missing_bins + 2)[1:-1].tolist()
                            bin_edges = sorted(list(set(bin_edges + temp_bins)))
                    
                elif binning_method == 'equal':
                    # Equal interval bins
                    bin_edges = np.linspace(min_val, max_val, n_bins + 1).tolist()
                    
                    # Handle the case where all values are the same
                    if min_val == max_val:
                        epsilon = 1e-10 * max(1, abs(min_val))
                        bin_edges = [min_val - epsilon]
                        for i in range(n_bins):
                            bin_edges.append(min_val + (i + 1) * epsilon)
                else:
                    # Default to equal interval if unknown method
                    print(f"Warning: Unknown binning method '{binning_method}', falling back to equal intervals")
                    bin_edges = np.linspace(min_val, max_val, n_bins + 1).tolist()
                
                # Ensure we have exactly n_bins+1 bin edges (for n_bins)
                # and they cover the entire range of data
                if not bin_edges or len(bin_edges) != n_bins + 1:
                    print(f"Warning: Bin edge calculation failed, using equal interval fallback")
                    bin_edges = np.linspace(min_val, max_val + 1e-9, n_bins + 1).tolist()
                
                # Make sure bin edges are strictly increasing
                for i in range(len(bin_edges) - 1):
                    if bin_edges[i] >= bin_edges[i+1]:
                        bin_edges[i+1] = bin_edges[i] + 1e-9
                
                # Create bin categories
                bin_col = f"{measure_name}_bin"
                bin_categories = pd.cut(
                    plot_data[measure_name],
                    bins=bin_edges,
                    labels=bin_labels,
                    include_lowest=True
                )
                
                # Store the bin edges and method for the legend
                measures[measure_name]['bin_edges'] = bin_edges
                measures[measure_name]['binning_method'] = binning_method
                
                # Convert to string to avoid dtype incompatibility with categorical plotting
                plot_data[bin_col] = bin_categories.astype(str)

            except Exception as e:
                print(f"Warning: Issue computing {binning_method} breaks for {measure_name}: {e}")
                # Fallback to simple equal interval bins
                min_val = non_nan_data[measure_name].min()
                max_val = non_nan_data[measure_name].max()
                
                if min_val == max_val:  # All values are identical
                    epsilon = 1e-10 * max(1, abs(min_val))
                    bin_edges = [min_val - epsilon]
                    for i in range(n_bins):
                        bin_edges.append(min_val + (i + 1) * epsilon)
                else:
                    bin_edges = np.linspace(min_val, max_val + 1e-9, n_bins + 1).tolist()
                
                # Create bin categories
                bin_col = f"{measure_name}_bin"
                bin_categories = pd.cut(
                    plot_data[measure_name],
                    bins=bin_edges,
                    labels=bin_labels,
                    include_lowest=True
                )
                
                # Store bin edges and method
                measures[measure_name]['bin_edges'] = bin_edges
                measures[measure_name]['binning_method'] = 'equal'  # Fallback method
                
                # Convert to string
                plot_data[bin_col] = bin_categories.astype(str)

    # Find global min and max for each measure for consistent sizing/coloring
    for measure_name in measures.keys():
        non_nan_data = plot_data[plot_data[measure_name].notna()]

        if len(non_nan_data) > 0:
            min_val = non_nan_data[measure_name].min()
            max_val = non_nan_data[measure_name].max()
            data_range = max_val - min_val

            measures[measure_name]['vmin'] = min_val
            measures[measure_name]['vmax'] = max_val

            # Adjust size_factor based on data range
            if plot_type in ['size', 'both']:
                # Scale size factor based on the data range to ensure consistent visuals
                base_size = measures[measure_name]['size_factor']
                if data_range > 0:
                    if aggregation == 'h3':
                        # H3 cells are polygons, so we use a different sizing approach
                        # Ensure log argument is positive
                        measures[measure_name]['size_factor'] = base_size / (10 * np.log10(data_range + 1 + 1e-9))
                    else:
                        # For point data, scale inversely with the data range
                        measures[measure_name]['size_factor'] = base_size / (np.sqrt(data_range) + 1e-9)
                else:
                    # If all values are the same, use a fixed size
                    measures[measure_name]['size_factor'] = 10
        else:
            print(f"Warning: No valid data for measure '{measure_name}' for min/max calculation.")
            measures[measure_name]['vmin'] = 0
            measures[measure_name]['vmax'] = 1

    # Plot each category
    for idx, category in enumerate(categories):
        ax = axes[idx]

        # Ensure all spines are hidden for all plots
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Plot boundary if provided
        if boundary_gdf is not None:
            boundary_gdf.boundary.plot(ax=ax, color='lightgrey', alpha=0.9, linewidth=1)

        # Filter data for this category
        if category != 'All Data' and 'category' in plot_data.columns:
            category_data = plot_data[plot_data['category'] == category]
        else:
            category_data = plot_data

        # Plot each measure according to the specified plot type
        for i, (measure_name, measure_opts) in enumerate(measures.items()):
            vmin = measure_opts['vmin']
            vmax = measure_opts['vmax']
            cmap = measure_opts['cmap']
            alpha = measure_opts['alpha']
            size_factor = measure_opts['size_factor']
            label_name = measure_opts.get('label_name', measure_name)

            # Skip if no data for this measure in this category (prevents empty plots)
            if len(category_data) == 0 or not category_data[measure_name].notna().any():
                continue

            if plot_type == 'color' or (plot_type == 'both' and aggregation == 'h3'):
                # Plot with choropleth colors based on bins
                bin_col = f"{measure_name}_bin"
                
                # Use custom colors for nrEvents or Blues colormap
                if measure_name == 'nrEvents' or cmap == 'Blues':
                    # Get the unique categories in the bin column, ensuring they're sorted in the right order
                    # The bin values will be B1, B2, B3, B4 so we need to sort them numerically
                    unique_bins = sorted(category_data[bin_col].unique(), 
                                         key=lambda x: int(x[1:]) if isinstance(x, str) and x[0] == 'B' and x[1:].isdigit() else 0)
                    n_bins = len(unique_bins)
                    custom_blues = ['#E3F6FD', '#75CCEC', '#089BD4', '#0169A1', '#023B6F']
                    # Create a color dictionary mapping each bin to its color
                    color_dict = {bin_val: custom_blues[i] for i, bin_val in enumerate(unique_bins)}
                    # Plot with custom colors
                    for bin_val, color in color_dict.items():
                        mask = category_data[bin_col] == bin_val
                        if mask.any():
                            category_data[mask].plot(
                                ax=ax,
                                color=color,
                                alpha=alpha,
                                legend=False
                            )
                else:
                    # Use standard colormap for other measures
                    category_data.plot(
                        ax=ax,
                        column=bin_col,
                        categorical=True,
                        cmap=cmap,
                        alpha=alpha,
                        legend=False
                    )

            elif plot_type == 'size' or (plot_type == 'both' and aggregation in ['latlon', 'admin']):
                # Use a more controlled approach to sizing that works better with outliers
                if vmax > vmin:  # Only if we have a valid range
                    # Add a small constant to handle zeros and prevent log(0)
                    epsilon = (vmax - vmin) * 0.01 if vmax > vmin else 0.1
                    
                    # Get log-transformed values (ensure positive input for log1p)
                    # Shift values so min_val becomes 0 for log transformation
                    log_vals = np.log1p((category_data[measure_name] - vmin) + epsilon)
                    log_max = np.log1p((vmax - vmin) + epsilon)
                    
                    # Scale to a reasonable marker size range (3 to 15)
                    min_marker_size = 3
                    max_marker_size = 15
                    sizes = min_marker_size + (log_vals / (log_max + 1e-9)) * (max_marker_size - min_marker_size)
                    
                    # Ensure sizes are not NaN if input was NaN
                    sizes = sizes.fillna(0) # or some default small size
                else:
                    # Fallback for when all values are the same (or range is zero)
                    sizes = np.ones(len(category_data)) * 5 # Fixed small size

                # Plot with bubble sizes
                category_data.plot(
                    ax=ax,
                    color=plt.cm.get_cmap(cmap)(0.6),  # Use a fixed color from the colormap
                    alpha=alpha,
                    markersize=sizes,
                    zorder=2 # Ensure bubbles are on top of choropleth if any
                )

            elif plot_type == 'both':
                # Both size and color for a single measure
                norm = Normalize(vmin=vmin, vmax=vmax)

                # For combined plots, we need to handle sizing and coloring
                # Determine if plotting polygons (H3) or points (latlon/admin)
                if aggregation == 'h3':
                    # First plot the polygons for color
                    bin_col = f"{measure_name}_bin"
                    
                    # Use custom colors for nrEvents or Blues colormap
                    if measure_name == 'nrEvents' or cmap == 'Blues':
                        # Get the unique categories in the bin column, ensuring they're sorted in the right order
                        # The bin values will be B1, B2, B3, B4 so we need to sort them numerically
                        unique_bins = sorted(category_data[bin_col].unique(), 
                                             key=lambda x: int(x[1:]) if isinstance(x, str) and x[0] == 'B' and x[1:].isdigit() else 0)
                        n_bins = len(unique_bins)
                        custom_blues = ['#E3F6FD', '#75CCEC', '#089BD4', '#0169A1', '#023B6F']
                        # Create a color dictionary mapping each bin to its color
                        color_dict = {bin_val: custom_blues[i] for i, bin_val in enumerate(unique_bins)}
                        # Plot with custom colors
                        for bin_val, color in color_dict.items():
                            mask = category_data[bin_col] == bin_val
                            if mask.any():
                                category_data[mask].plot(
                                    ax=ax,
                                    color=color,
                                    alpha=alpha,
                                    legend=False
                                )
                    else:
                        # Use standard colormap for other measures
                        category_data.plot(
                            ax=ax,
                            column=bin_col,
                            categorical=True,
                            cmap=cmap,
                            alpha=alpha,
                            legend=False
                        )
                    # Then plot centroids as sized markers
                    for _, row in category_data.iterrows():
                        if pd.notna(row[measure_name]):
                            value = row[measure_name]
                            normalized_value = (value - vmin) / (vmax - vmin + 1e-10)
                            marker_color = plt.cm.get_cmap(cmap)(normalized_value)
                            
                            centroid = row.geometry.centroid
                            
                            epsilon_size = (vmax - vmin) * 0.01 if vmax > vmin else 0.1
                            log_val_size = np.log1p((value - vmin) + epsilon_size)
                            log_max_size = np.log1p((vmax - vmin) + epsilon_size)
                            marker_size = 3 + (log_val_size / (log_max_size + 1e-9)) * 12
                            
                            ax.plot(
                                centroid.x, centroid.y,
                                'o',
                                color=marker_color,
                                alpha=alpha,
                                markersize=marker_size,
                                zorder=3 # Ensure markers are on top
                            )
                else: # aggregation is 'latlon' or 'admin' (point-based plotting)
                    for _, row in category_data.iterrows():
                        if pd.notna(row[measure_name]):
                            value = row[measure_name]
                            normalized_value = (value - vmin) / (vmax - vmin + 1e-10)
                            marker_color = plt.cm.get_cmap(cmap)(normalized_value)
                            
                            epsilon_size = (vmax - vmin) * 0.01 if vmax > vmin else 0.1
                            log_val_size = np.log1p((value - vmin) + epsilon_size)
                            log_max_size = np.log1p((vmax - vmin) + epsilon_size)
                            marker_size = 3 + (log_val_size / (log_max_size + 1e-9)) * 12
                            
                            ax.plot(
                                row.geometry.x, row.geometry.y,
                                'o',
                                color=marker_color,
                                alpha=alpha,
                                markersize=marker_size,
                                zorder=3
                            )

        # Set title for each subplot (category)
        ax.set_title(category, y=1.0, pad=10, fontfamily=font_choice)

        # Ensure all ticks and spines are completely removed (redundant but safe)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.tick_params(left=False, right=False, bottom=False, top=False,
                       labelleft=False, labelright=False, labelbottom=False, labeltop=False)
        for spine in ax.spines.values():
            spine.set_visible(False)


    # --- Legend Creation ---
    legend_items = []

    # Combine all unique measures for legend creation
    for measure_name, measure_opts in measures.items():
        label_name = measure_opts.get('label_name', measure_name)

        if plot_type == 'color' or (plot_type == 'both' and aggregation == 'h3'):
            # Create color legend for binned data
            # Use custom blue colors provided for specific cases
            custom_blues = ['#E3F6FD', '#75CCEC', '#089BD4', '#0169A1', '#023B6F']
            n_bins = len(measure_opts['bin_edges']) - 1 if 'bin_edges' in measure_opts else 4
            
            # Always use custom blues for nrEvents or if blues is specified
            if measure_name == 'nrEvents' or cmap == 'Blues':
                # Make sure we have enough colors
                if n_bins > len(custom_blues):
                    # If we need more bins than colors, interpolate additional colors
                    colors = custom_blues
                else:
                    # Otherwise use the exact colors specified
                    colors = custom_blues[:n_bins]
                    
                # Store original order to ensure legend matches plot
                colors_ordered = colors.copy()
            else:
                # For other measures, use the specified colormap
                cmap = plt.cm.get_cmap(measure_opts['cmap'])
                colors = [cmap(x) for x in np.linspace(0.2, 0.8, n_bins)]
            
            # Get the binning method used
            binning_method = measure_opts.get('binning_method', 'equal')
            method_name = {
                'jenks': 'Jenks Natural Breaks', 
                'quantile': 'Quantiles', 
                'equal': 'Equal Intervals'
            }.get(binning_method, binning_method.capitalize())

            if 'bin_edges' in measure_opts and len(measure_opts['bin_edges']) >= 2:
                bin_edges = measure_opts['bin_edges']
                
                # Store method name to be added to the source text later
                if label_name:
                    method_label = f"{label_name} ({method_name})"
                else:
                    method_label = f"{method_name}"
                
                # Store method info to add to source text
                measure_opts['method_label'] = method_label
                
                # Add legend items for each bin
                for i in range(len(bin_edges) - 1):
                    # Format legend labels to avoid scientific notation for small numbers unless necessary
                    lower_bound = f"{bin_edges[i]:.1f}" if abs(bin_edges[i]) >= 0.01 or bin_edges[i] == 0 else f"{bin_edges[i]:.1e}"
                    upper_bound = f"{bin_edges[i+1]:.1f}" if abs(bin_edges[i+1]) >= 0.01 or bin_edges[i+1] == 0 else f"{bin_edges[i+1]:.1e}"
                    
                    # Get the color - use ordered colors for custom blue palettes
                    if measure_name == 'nrEvents' or cmap == 'Blues':
                        color = colors_ordered[i]
                    else:
                        color = colors[i]
                    
                    legend_items.append(
                        Patch(
                            facecolor=color,
                            edgecolor='none',
                            alpha=measure_opts['alpha'],
                            label=f"{lower_bound} - {upper_bound}"
                        )
                    )
            else: # Fallback for legend if bin_edges not properly calculated
                legend_items.append(
                    Patch(
                        facecolor=colors[0],
                        edgecolor='none',
                        alpha=measure_opts['alpha'],
                        label=f"{label_name} (Categorical)"
                    )
                )

        if plot_type == 'size' or plot_type == 'both': # For size legend, always consider
            vmin = measure_opts['vmin']
            vmax = measure_opts['vmax']

            if vmax > vmin: # Only create size legend if data range is valid
                # Create a few representative size values for the legend
                size_values_for_legend = np.linspace(vmin, vmax, 3) # e.g., min, mid, max
                size_labels = [f"{label_name}: {val:.2f}" for val in size_values_for_legend] # Format
                
                epsilon_size = (vmax - vmin) * 0.01 if vmax > vmin else 0.1
                log_values_for_legend = [np.log1p((val - vmin) + epsilon_size) for val in size_values_for_legend]
                log_max_size = np.log1p((vmax - vmin) + epsilon_size)
                
                min_marker_size = 3
                max_marker_size = 15
                marker_sizes_for_legend = [min_marker_size + (log_val / (log_max_size + 1e-9)) * (max_marker_size - min_marker_size)
                                           for log_val in log_values_for_legend]

                for ms, label in zip(marker_sizes_for_legend, size_labels):
                    # Use a fixed color for size legend, typically the midpoint of the cmap or a neutral color
                    legend_items.append(
                        Line2D(
                            [0], [0],
                            marker='o',
                            color='w',
                            markerfacecolor=plt.cm.get_cmap(measure_opts['cmap'])(0.6),
                            markeredgecolor='gray', # Add edge for clarity
                            markersize=ms,
                            alpha=measure_opts['alpha'],
                            label=label
                        )
                    )
            else: # If all size values are the same, show one representative size
                legend_items.append(
                    Line2D(
                        [0], [0],
                        marker='o',
                        color='w',
                        markerfacecolor=plt.cm.get_cmap(measure_opts['cmap'])(0.6),
                        markeredgecolor='gray',
                        markersize=5, # Default size
                        alpha=measure_opts['alpha'],
                        label=f"{label_name}: {vmin:.2f} (All Same)"
                    )
                )

    # --- Legend Positioning based on Layout ---
    if legend_items:
        if layout == 'columns':
            # Horizontal layout, legend at bottom
            legend_loc = 'lower center'
            legend_ncol = min(4, len(legend_items)) # Limit legend columns
            # adjust bbox_to_anchor to avoid overlap with source text
            legend_bbox_to_anchor = (0.5, 0.12)
            # Adjust subplots_adjust to make space at the bottom
            bottom_margin = 0.25
            right_margin = 0.85
        else: # layout == 'rows'
            # Vertical layout, legend on the right
            legend_loc = 'lower right'
            legend_ncol = 1 # Stack legend items vertically, or 2 if many
            # # Adjust bbox_to_anchor to position it to the right of the last subplot
            # # (1.05, 0.5) places it slightly outside the right edge, vertically centered
            legend_bbox_to_anchor = (1.05, 0.1)
            # Adjust subplots_adjust to make space on the right
            bottom_margin = 0.1
            right_margin = 0.8 # Increase right margin to make space for legend
            # If categories are many, you might need to adjust figsize to be wider
            # or make subplots_adjust more aggressive on right margin
            if n_categories > 3: # Heuristic for potentially crowded vertical layouts
                right_margin = 0.75 # More space for legend

        legend = fig.legend(
            handles=legend_items,
            loc='lower left',  # Left-aligned legend
            frameon=False,  # Remove frame around legend
            ncol=legend_ncol,
            bbox_to_anchor=(0.05, 0.12),  # Position at lower left
            bbox_transform=fig.transFigure, # Crucial for fig.legend with bbox_to_anchor
            columnspacing=1.0,  # Adjust spacing between legend columns
            handletextpad=0.5   # Reduce padding between color box and text
        )
        
        # Adjust font size and style for legend items
        for i, text in enumerate(legend.get_texts()):
            # Set font size based on item type
            if i == 0:  # Method name (header)
                text.set_fontsize(10)
                text.set_fontweight('bold')
            else:  # Regular bin items
                text.set_fontsize(9)
                
        # Adjust legend item spacing
        legend.get_frame().set_linewidth(0.5)  # Thinner border


    # Set main title
    fig.suptitle(title, fontsize=16, y=0.95, fontfamily=font_choice, fontweight='bold')

    # Add source text box at the bottom (position relative to figure)
    today = datetime.now().strftime("%B %d, %Y")
    
    # Check if we have any method labels to add to source text
    method_labels = []
    for measure_name, measure_opts in measures.items():
        if 'method_label' in measure_opts:
            method_labels.append(measure_opts['method_label'])
    
    # Build source text with method name if available
    if method_labels:
        method_text = f" - {', '.join(method_labels)}"
        source_text = f"Source: ACLED. Accessed: {today}{method_text}"
    else:
        source_text = f"Source: ACLED. Accessed: {today}"
    
    # Adjust source text position based on legend placement
    if layout == 'columns':
        fig.text(0.5, 0.02, source_text, ha='center', fontsize=9, fontfamily=font_choice)
    else: # layout == 'rows'
        # Place source text below the plots, aligning with the left edge of plots
        fig.text(0.05, 0.02, source_text, ha='left', fontsize=9, fontfamily=font_choice)


    # Adjust layout to ensure equal spacing and size
    plt.subplots_adjust(bottom=bottom_margin, top=0.85, wspace=0.05, hspace=0.05, right=right_margin)

    return fig, axes


# Define a global or function-level COLOR_PALETTE (as it's used in your code)
COLOR_PALETTE = Category10[10] # Using a standard Bokeh palette

from bokeh.plotting import figure, show
from bokeh.models import Span, Label, Legend, ColumnDataSource, HoverTool
from bokeh.layouts import column
from bokeh.palettes import Category10
import pandas as pd
import numpy as np
from datetime import datetime

# Define a global or function-level COLOR_PALETTE
COLOR_PALETTE = Category10[10]

def plot_conflict_metrics_by_country(
    data: pd.DataFrame,
    metrics_to_plot: list,
    metric_display_info: dict = None,
    sorting_metric: str = None,
    overall_title: str = 'Comparison of Metrics by Country',
    source_text: str = None,
    figsize: tuple = (15, 8)
) -> plt.Figure:
    """
    Generates a horizontally concatenated bar chart for specified metrics by country,
    with text labels for values using matplotlib.

    Args:
        data (pd.DataFrame): The input DataFrame containing 'country' and metric columns.
        metrics_to_plot (list): A list of column names (metrics) to visualize.
        metric_display_info (dict, optional): A dictionary mapping metric names to
            dictionaries with 'title' and 'color' keys.
        sorting_metric (str, optional): The name of the metric to use for sorting.
        overall_title (str, optional): The main title for the concatenated chart.
        source_text (str, optional): Text to be displayed as a subtitle.
        figsize (tuple, optional): Figure size (width, height). Defaults to (15, 8).

    Returns:
        plt.Figure: A matplotlib Figure object.
    """
    
    if metric_display_info is None:
        metric_display_info = {}

    # Sort the data if a sorting_metric is provided
    if sorting_metric and sorting_metric in data.columns:
        if pd.api.types.is_numeric_dtype(data[sorting_metric]):
            data_sorted = data.sort_values(by=sorting_metric, ascending=True).reset_index(drop=True)
            print(f"Sorting countries by '{sorting_metric}' in ascending order.")
        else:
            data_sorted = data.copy()
            print(f"Warning: Sorting metric '{sorting_metric}' is not numeric.")
    else:
        data_sorted = data.copy()
        if sorting_metric:
            print(f"Warning: Sorting metric '{sorting_metric}' not found.")

    # Filter valid metrics
    valid_metrics = [m for m in metrics_to_plot if m in data_sorted.columns]
    if not valid_metrics:
        print("No valid metrics found in the DataFrame.")
        return None

    n_metrics = len(valid_metrics)
    
    # Create figure and subplots
    fig, axes = plt.subplots(1, n_metrics, figsize=figsize, sharey=True)
    
    # Handle single subplot case
    if n_metrics == 1:
        axes = [axes]
    
    # Set overall style
    plt.style.use('default')
    fig.patch.set_facecolor('white')
    
    countries = data_sorted['country'].values
    y_pos = np.arange(len(countries))
    
    for i, metric in enumerate(valid_metrics):
        ax = axes[i]
        
        # Get custom title and color, or use defaults
        display_info = metric_display_info.get(metric, {})
        metric_title = display_info.get('title', metric)
        metric_color = display_info.get('color', '#1f77b4')  # Default blue
        
        values = data_sorted[metric].values
        
        # Create horizontal bar chart
        bars = ax.barh(y_pos, values, color=metric_color, alpha=0.8, 
                       edgecolor='white', linewidth=0.5)
        
        # Add value labels on bars
        for j, (bar, value) in enumerate(zip(bars, values)):
            width = bar.get_width()
            # Position text slightly to the right of bar end
            ax.text(width + max(values) * 0.01, bar.get_y() + bar.get_height()/2, 
                    f'{int(value):,}', ha='left', va='center', fontsize=9, 
                    fontweight='bold', color='black')
        
        # Customize subplot
        ax.set_yticks(y_pos)
        ax.set_xlabel(f'Number of {metric_title}', fontsize=11, fontweight='bold')
        ax.set_title(f'{metric_title} by Country', fontsize=12, fontweight='bold', pad=15)
        
        # Only show y-axis labels on leftmost subplot
        if i > 0:
            ax.set_yticklabels([])
        else:
            ax.set_yticklabels(countries, fontsize=10)
            ax.set_ylabel('Country', fontsize=11, fontweight='bold')
        
        # Style the subplot
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#CCCCCC')
        ax.spines['bottom'].set_color('#CCCCCC')
        ax.tick_params(colors='#666666')
        ax.grid(axis='x', alpha=0.3, linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)
        
        # Set x-axis to start from 0 and add some padding
        ax.set_xlim(0, max(values) * 1.15)
    
    # Add overall title
    fig.suptitle(overall_title, fontsize=16, fontweight='bold', y=0.95)
    
    # Add source text as subtitle
    if source_text:
        fig.text(0.5, 0.02, source_text, ha='center', va='bottom', 
                 fontsize=9, style='italic', color='#666666')
    
    # Adjust layout
    plt.tight_layout()
    # Ensure enough space for y-axis labels on the left
    plt.subplots_adjust(left=0.15, top=0.88, bottom=0.1 if source_text else 0.05)
    
    return fig
