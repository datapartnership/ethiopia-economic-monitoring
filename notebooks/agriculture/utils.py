"""
Utility functions for diff-in-diff analysis of conflict and agricultural output.

This module provides helper functions for data processing and categorization
used in the Ethiopia conflict and agricultural monitoring analysis.
"""

import pandas as pd
import numpy as np


def get_conflict_time_categories(conflict_adm3, baseline_year, end_year=None):
    """
    Categorize conflict events into pre and post treatment periods.
    
    Parameters:
    -----------
    conflict_adm3 : DataFrame
        Conflict data with columns ['ADM3_EN', 'ADM2_EN', 'date', 'nrEvents', 'nrFatalities']
    baseline_year : int
        Year that splits pre/post periods (pre: <=baseline_year, post: >baseline_year)
    end_year : int, optional
        Last year to include in analysis (filters out data after this year)
        
    Returns:
    --------
    DataFrame with conflict counts by region and time category
    """
    conflict_adm3_cat = conflict_adm3.copy()
    conflict_adm3_cat['year'] = conflict_adm3_cat['date'].dt.year
    
    # Filter by end_year if provided
    if end_year is not None:
        conflict_adm3_cat = conflict_adm3_cat[conflict_adm3_cat['year'] <= end_year]
    
    conflict_adm3_cat['time_category'] = conflict_adm3_cat['year'].apply(
        lambda x: 'Pre-Conflict' if x <= baseline_year else 'Post-Conflict'
    )

    conflict_adm3_cat = conflict_adm3_cat.groupby(['ADM3_EN', 'time_category', 'ADM2_EN'])[['nrEvents', 'nrFatalities']].sum().reset_index()
    conflict_adm3_cat['conflict_index'] = np.sqrt(conflict_adm3_cat['nrEvents'] * (1+conflict_adm3_cat['nrFatalities']))
    #conflict_adm3_tot = conflict_adm3_cat.groupby(['ADM3_EN', 'ADM2_EN'])[['nrEvents', 'nrFatalities']].sum().reset_index()

    return conflict_adm3_cat


def categorize_conflict_regions(all_adm3, conflict_df, 
                                conflict_threshold=10, 
                                treatment_year=2019, 
                                end_year=2025, 
                                conflict_metric='nrFatalities'):
    """
    Categorize regions based on conflict patterns before and after treatment year.
    
    Parameters:
    -----------
    all_adm3 : list
        List of all ADM3 region names to categorize
    conflict_adm3_cat : DataFrame
        DataFrame with columns ['ADM3_EN', 'time_category', conflict_metric]
        Must be created using get_conflict_time_categories() with matching baseline_year and end_year
    conflict_threshold : int, default=10
        Threshold value to classify as high/low conflict
    treatment_year : int, default=2019
        Year when treatment starts (used for display only - data split must match)
    end_year : int, default=2025
        Last year of analysis (used for display only)
    conflict_metric : str, default='nrFatalities'
        Column name to use for conflict measurement ('nrFatalities', 'nrEvents', or other)
        
    Returns:
    --------
    new_conflict : list
        Regions with conflict escalation (pre<=threshold, post>threshold)
    persistent_conflict : list
        Regions with sustained high conflict (both>threshold)
    reduced_conflict : list
        Regions with conflict reduction (pre>threshold, post<=threshold)
    no_conflict : list
        Regions with no conflict (not in database)
    low_conflict_list : list
        Regions with low conflict (both<=threshold)
    """
    new_conflict = []
    persistent_conflict = []
    reduced_conflict = []
    no_conflict = []
    low_conflict_list = []

    conflict_adm3_cat = get_conflict_time_categories(conflict_df,
                                                    baseline_year=treatment_year,
                                                     end_year=end_year
                                                     )

    for adm3 in all_adm3:
        # Check if this region has any conflict data
        if adm3 not in conflict_adm3_cat['ADM3_EN'].values:
            # Region has no conflict data at all - add to no_conflict
            no_conflict.append(adm3)
            continue
        
        df = conflict_adm3_cat[conflict_adm3_cat['ADM3_EN']==adm3]
        
        # Get data for both time periods using the specified conflict metric
        post_conflict_data = df[df['time_category']=='Post-Conflict'][conflict_metric]
        pre_conflict_data = df[df['time_category']=='Pre-Conflict'][conflict_metric]
        
        # Get values (0 if no data for that period - treat as no conflict)
        post_value = post_conflict_data.values[0] if len(post_conflict_data) > 0 else 0
        pre_value = pre_conflict_data.values[0] if len(pre_conflict_data) > 0 else 0
        
        # Categorize based on conflict patterns
        if post_value > conflict_threshold and pre_value <= conflict_threshold:
            # New conflict: low/no conflict before (<=threshold), high conflict after (>threshold)
            # This includes regions with conflict only in post period
            new_conflict.append(adm3)
        elif pre_value > conflict_threshold and post_value <= conflict_threshold:
            # Reduced conflict: high conflict before (>threshold), low/no conflict after (<=threshold)
            # This includes regions with conflict only in pre period
            reduced_conflict.append(adm3)
        elif post_value > conflict_threshold and pre_value > conflict_threshold:
            # Persistent conflict (>threshold in both periods)
            persistent_conflict.append(adm3)
        else:
            # Low conflict: both periods have <=threshold
            # This catches regions with <=threshold in both periods even if total > threshold
            low_conflict_list.append(adm3)

    print(f"\n=== Conflict Categories (threshold={conflict_threshold} {conflict_metric}, treatment year={treatment_year}, period: up to {end_year}, excluding bottom quartile crop area) ===")
    print(f"No conflict (not in conflict database): {len(no_conflict)}")
    print(f"Low conflict (<={conflict_threshold} {conflict_metric} per period): {len(low_conflict_list)}")
    print(f"New conflict (pre<={conflict_threshold}, post>{conflict_threshold}): {len(new_conflict)}")
    print(f"Reduced conflict (pre>{conflict_threshold}, post<={conflict_threshold}): {len(reduced_conflict)}")
    print(f"Persistent conflict (>{conflict_threshold} {conflict_metric} both periods): {len(persistent_conflict)}")
    print(f"\nTotal categorized: {len(no_conflict) + len(low_conflict_list) + len(new_conflict) + len(reduced_conflict) + len(persistent_conflict)}")
    print(f"Difference from filtered total: {len(all_adm3) - (len(no_conflict) + len(low_conflict_list) + len(new_conflict) + len(reduced_conflict) + len(persistent_conflict))}")

    # Check for overlaps between lists
    print("\n=== Checking for overlaps ===")
    all_lists = {
        'no_conflict': set(no_conflict),
        'low_conflict': set(low_conflict_list),
        'new_conflict': set(new_conflict),
        'reduced_conflict': set(reduced_conflict),
        'persistent_conflict': set(persistent_conflict)
    }

    overlaps_found = False
    for name1, list1 in all_lists.items():
        for name2, list2 in all_lists.items():
            if name1 < name2:  # Compare each pair only once
                overlap = list1 & list2
                if overlap:
                    print(f"OVERLAP between {name1} and {name2}: {len(overlap)} regions")
                    print(f"  Regions: {sorted(list(overlap))[:5]}{'...' if len(overlap) > 5 else ''}")
                    overlaps_found = True

    if not overlaps_found:
        print("No overlaps found - all regions are uniquely categorized!")

    return new_conflict, persistent_conflict, reduced_conflict, no_conflict, low_conflict_list


def create_did_regression_table(results_list, model_data_list, model_names, 
                                 title='Dependent variable: EVI (Enhanced Vegetation Index)',
                                 subtitle='Treatment Period: 2019 onwards; Entity and Time Fixed Effects Included',
                                 treatment_var='treated_post',
                                 treatment_col='NewConflict',
                                 control_col='NewConflict',
                                 region_col='ADM3_EN'):
    """
    Create an academic-style regression comparison table for multiple DiD models.
    
    Parameters
    ----------
    results_list : list
        List of PanelOLS regression results (e.g., [result1, result2, result3])
    model_data_list : list
        List of DataFrames containing model data (e.g., [model1, model2, model3])
    model_names : dict or list
        If dict: {'model1_name': 'Name 1', 'model2_name': 'Name 2', ...}
        If list: ['Name 1', 'Name 2', 'Name 3']
    title : str, optional
        Title for the table
    subtitle : str, optional
        Subtitle describing the specification
    treatment_var : str, optional
        Name of the treatment variable to add confidence intervals for
    treatment_col : str, optional
        Column name for treatment indicator (1 for treatment, 0 for control)
    control_col : str, optional
        Column name for control indicator (same as treatment_col typically)
    region_col : str, optional
        Column name for region identifier
        
    Returns
    -------
    pd.DataFrame
        DataFrame containing the formatted regression table with metadata attributes
    """
    import pandas as pd
    
    # Convert model_names to dict if it's a list
    if isinstance(model_names, list):
        model_names_dict = {f'model{i+1}_name': name for i, name in enumerate(model_names)}
    else:
        model_names_dict = model_names
    
    # Get column names from model_names dict
    col_names = [model_names_dict[key] for key in sorted(model_names_dict.keys())]
    
    # Create regression table
    regression_table = []
    
    # Get all unique variable names from all results
    all_variables = []
    for result in results_list:
        all_variables.extend(result.params.index.tolist())
    # Remove duplicates while preserving order
    variables = list(dict.fromkeys(all_variables))
    
    for var in variables:
        # Coefficient row
        coef_row = {'Variable': var}
        
        for i, (result, col_name) in enumerate(zip(results_list, col_names)):
            if var in result.params.index:
                coef = result.params[var]
                pval = result.pvalues[var]
                stars = '***' if pval < 0.01 else ('**' if pval < 0.05 else ('*' if pval < 0.1 else ''))
                coef_row[col_name] = f"{coef:.4f}{stars}"
            else:
                coef_row[col_name] = ''
        
        regression_table.append(coef_row)
        
        # Standard error row
        se_row = {'Variable': ''}
        
        for i, (result, col_name) in enumerate(zip(results_list, col_names)):
            if var in result.params.index:
                se = result.std_errors[var]
                se_row[col_name] = f"({se:.4f})"
            else:
                se_row[col_name] = ''
        
        regression_table.append(se_row)
        
        # Add 95% CI row for treatment variable only
        if var == treatment_var:
            ci_row = {'Variable': '[95% CI]'}
            
            for i, (result, col_name) in enumerate(zip(results_list, col_names)):
                if var in result.params.index:
                    ci = result.conf_int().loc[var]
                    ci_row[col_name] = f"[{ci.iloc[0]:.4f}, {ci.iloc[1]:.4f}]"
                else:
                    ci_row[col_name] = ''
            
            regression_table.append(ci_row)
    
    # Add model statistics
    empty_row = {'Variable': ''}
    for col_name in col_names:
        empty_row[col_name] = ''
    regression_table.append(empty_row)
    
    # Observations
    obs_row = {'Variable': 'Observations'}
    for model_data, col_name in zip(model_data_list, col_names):
        obs_row[col_name] = f"{len(model_data):,}"
    regression_table.append(obs_row)
    
    # R²
    r2_row = {'Variable': 'R²'}
    for result, col_name in zip(results_list, col_names):
        r2_row[col_name] = f"{result.rsquared:.4f}"
    regression_table.append(r2_row)
    
    # Treatment Regions
    treat_row = {'Variable': 'Treatment Regions'}
    for model_data, col_name in zip(model_data_list, col_names):
        treat_row[col_name] = f"{model_data[model_data[treatment_col]==1][region_col].nunique()}"
    regression_table.append(treat_row)
    
    # Control Regions
    control_row = {'Variable': 'Control Regions'}
    for model_data, col_name in zip(model_data_list, col_names):
        control_row[col_name] = f"{model_data[model_data[control_col]==0][region_col].nunique()}"
    regression_table.append(control_row)
    
    # Clustered SE
    cluster_row = {'Variable': 'Clustered SE'}
    for col_name in col_names:
        cluster_row[col_name] = 'Region'
    regression_table.append(cluster_row)
    
    # Create DataFrame
    reg_df = pd.DataFrame(regression_table)
    
    # Add table metadata as attributes
    reg_df.attrs['title'] = title
    reg_df.attrs['subtitle'] = subtitle
    reg_df.attrs['model_names'] = model_names_dict
    reg_df.attrs['note'] = '*p<0.1; **p<0.05; ***p<0.01. Standard errors in parentheses, clustered at region level.'
    
    return reg_df


def find_similar_climate_regions(region_list, lst_data, rainfall_data, evi_data=None, elevation_data=None, n_clusters=5, 
                                  start_year=2012, end_year=2020, 
                                  method='kmeans', include_lst=True, include_rainfall=True, include_evi=True, include_elevation=True,
                                  lst_weight=0.25, rainfall_weight=0.25, evi_weight=0.25, elevation_weight=0.25, plot=False):
    """
    Use machine learning to identify regions with similar climate patterns (LST + rainfall + EVI + elevation) over time.
    
    Parameters
    ----------
    region_list : list
        List of ADM3 region names to analyze
    lst_data : DataFrame
        LST dataset with columns ['ADM3_EN', 'date', 'lst_mean', 'lst_max']
    rainfall_data : DataFrame
        Rainfall dataset with columns ['ADM3_EN', 'date', 'rainfall_mm']
    evi_data : DataFrame, optional
        EVI dataset with columns ['ADM3_EN', 'date', 'EVI']
    elevation_data : DataFrame, optional
        Elevation dataset with columns ['ADM3_EN', 'elevation_mean', 'elevation_std']
    n_clusters : int, default 5
        Number of clusters to identify
    start_year : int, default 2012
        Starting year for analysis
    end_year : int, default 2020
        Ending year for analysis
    method : str, default 'kmeans'
        Clustering method: 'kmeans', 'hierarchical', or 'dbscan'
    include_lst : bool, default True
        Whether to include LST data in clustering
    include_rainfall : bool, default True
        Whether to include rainfall data in clustering
    include_evi : bool, default True
        Whether to include EVI data in clustering
    include_elevation : bool, default True
        Whether to include elevation data in clustering
    lst_weight : float, default 0.25
        Weight for LST features (0-1)
    rainfall_weight : float, default 0.25
        Weight for rainfall features (0-1)
    evi_weight : float, default 0.25
        Weight for EVI features (0-1)
    elevation_weight : float, default 0.25
        Weight for elevation features (0-1)
    plot : bool, default False
        Whether to create visualization plots (deprecated - use plot_climate_clusters_time_series from visuals module)
    
    Returns
    -------
    clusters : dict
        Dictionary mapping cluster_id to list of regions
    cluster_df : DataFrame
        DataFrame with region and cluster assignment
    similarity_matrix : DataFrame
        Pairwise similarity matrix between regions
    feature_matrix : DataFrame
        Combined feature matrix used for clustering
        
    Examples
    --------
    >>> clusters, assignments, similarity, features = find_similar_climate_regions(
    ...     region_list=regions,
    ...     lst_data=lst,
    ...     rainfall_data=rainfall,
    ...     n_clusters=3,
    ...     start_year=2012,
    ...     end_year=2019
    ... )
    """
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans, DBSCAN
    from scipy.cluster.hierarchy import linkage, fcluster
    from sklearn.metrics import silhouette_score
    
    feature_dfs = []
    feature_names = []
    
    # Process LST data
    if include_lst:
        lst_filtered = lst_data[lst_data['ADM3_EN'].isin(region_list)].copy()
        lst_filtered['year'] = lst_filtered['date'].dt.year
        lst_filtered['month'] = lst_filtered['date'].dt.month
        lst_filtered = lst_filtered[(lst_filtered['year'] >= start_year) & (lst_filtered['year'] <= end_year)]
        
        # Create LST time series matrix
        lst_pivot = lst_filtered.pivot_table(
            index='ADM3_EN',
            columns=['year', 'month'],
            values='lst_mean',
            aggfunc='mean'
        )
        lst_pivot = lst_pivot.ffill(axis=1).bfill(axis=1)
        
        # Standardize and weight
        scaler_lst = StandardScaler()
        lst_scaled = scaler_lst.fit_transform(lst_pivot) * lst_weight
        lst_scaled_df = pd.DataFrame(lst_scaled, index=lst_pivot.index, 
                                      columns=[f'lst_{c[0]}_{c[1]}' for c in lst_pivot.columns])
        feature_dfs.append(lst_scaled_df)
        feature_names.append('LST')
        print(f"LST features: {lst_scaled_df.shape[1]} (weight: {lst_weight})")
    
    # Process Rainfall data
    if include_rainfall:
        rain_filtered = rainfall_data[rainfall_data['ADM3_EN'].isin(region_list)].copy()
        rain_filtered['year'] = rain_filtered['date'].dt.year
        rain_filtered['month'] = rain_filtered['date'].dt.month
        rain_filtered = rain_filtered[(rain_filtered['year'] >= start_year) & (rain_filtered['year'] <= end_year)]
        
        # Create rainfall time series matrix
        rain_pivot = rain_filtered.pivot_table(
            index='ADM3_EN',
            columns=['year', 'month'],
            values='rainfall_mm',
            aggfunc='mean'
        )
        rain_pivot = rain_pivot.ffill(axis=1).bfill(axis=1)
        
        # Standardize and weight
        scaler_rain = StandardScaler()
        rain_scaled = scaler_rain.fit_transform(rain_pivot) * rainfall_weight
        rain_scaled_df = pd.DataFrame(rain_scaled, index=rain_pivot.index,
                                       columns=[f'rain_{c[0]}_{c[1]}' for c in rain_pivot.columns])
        feature_dfs.append(rain_scaled_df)
        feature_names.append('Rainfall')
        print(f"Rainfall features: {rain_scaled_df.shape[1]} (weight: {rainfall_weight})")
    
    # Process EVI data
    if include_evi and evi_data is not None:
        evi_filtered = evi_data[evi_data['ADM3_EN'].isin(region_list)].copy()
        evi_filtered['year'] = evi_filtered['date'].dt.year
        evi_filtered['month'] = evi_filtered['date'].dt.month
        evi_filtered = evi_filtered[(evi_filtered['year'] >= start_year) & (evi_filtered['year'] <= end_year)]
        
        # Create EVI time series matrix
        evi_pivot = evi_filtered.pivot_table(
            index='ADM3_EN',
            columns=['year', 'month'],
            values='EVI',
            aggfunc='mean'
        )
        evi_pivot = evi_pivot.ffill(axis=1).bfill(axis=1)
        
        # Standardize and weight
        scaler_evi = StandardScaler()
        evi_scaled = scaler_evi.fit_transform(evi_pivot) * evi_weight
        evi_scaled_df = pd.DataFrame(evi_scaled, index=evi_pivot.index,
                                      columns=[f'evi_{c[0]}_{c[1]}' for c in evi_pivot.columns])
        feature_dfs.append(evi_scaled_df)
        feature_names.append('EVI')
        print(f"EVI features: {evi_scaled_df.shape[1]} (weight: {evi_weight})")
    
    # Process Elevation data
    if include_elevation and elevation_data is not None:
        elev_filtered = elevation_data[elevation_data['ADM3_EN'].isin(region_list)].copy()
        
        # Use elevation statistics as features
        elev_features = elev_filtered.set_index('ADM3_EN')[['elevation_mean', 'elevation_std']]
        
        # Standardize and weight
        scaler_elev = StandardScaler()
        elev_scaled = scaler_elev.fit_transform(elev_features) * elevation_weight
        elev_scaled_df = pd.DataFrame(elev_scaled, index=elev_features.index,
                                       columns=['elevation_mean', 'elevation_std'])
        feature_dfs.append(elev_scaled_df)
        feature_names.append('Elevation')
        print(f"Elevation features: {elev_scaled_df.shape[1]} (weight: {elevation_weight})")
    
    # Combine features
    if len(feature_dfs) == 0:
        raise ValueError("Must include at least one of LST, rainfall, EVI, or elevation data")
    
    # Find common regions across all datasets
    common_regions = feature_dfs[0].index
    for df in feature_dfs[1:]:
        common_regions = common_regions.intersection(df.index)
    
    print(f"\nAnalyzing {len(common_regions)} regions with complete data")
    print(f"Time period: {start_year}-{end_year}")
    print(f"Features: {' + '.join(feature_names)}")
        
    # Combine all features for common regions
    combined_features = pd.concat([df.loc[common_regions] for df in feature_dfs], axis=1)
    combined_features = combined_features.dropna(thresh=len(combined_features.columns) * 0.5)
    
    print(f"Final feature matrix: {combined_features.shape[0]} regions × {combined_features.shape[1]} features")
    
    # Use combined features as the data matrix
    X_scaled = combined_features.values
        
    # Apply clustering method
    if method == 'kmeans':
        clusterer = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = clusterer.fit_predict(X_scaled)
        
    elif method == 'hierarchical':
        # Compute linkage matrix
        linkage_matrix = linkage(X_scaled, method='ward')
        cluster_labels = fcluster(linkage_matrix, n_clusters, criterion='maxclust') - 1
        
    elif method == 'dbscan':
        clusterer = DBSCAN(eps=3, min_samples=2)
        cluster_labels = clusterer.fit_predict(X_scaled)
        n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
        print(f"DBSCAN identified {n_clusters} clusters (excluding noise)")
    
    else:
        raise ValueError(f"Unknown method: {method}. Choose 'kmeans', 'hierarchical', or 'dbscan'")
    
    # Calculate silhouette score
    if len(set(cluster_labels)) > 1:
        sil_score = silhouette_score(X_scaled, cluster_labels)
        print(f"Silhouette Score: {sil_score:.3f} (higher is better, range [-1, 1])")
    
    # Create cluster assignments
    cluster_df = pd.DataFrame({
        'ADM3_EN': combined_features.index,
        'cluster': cluster_labels
    })
    
    # Group regions by cluster
    clusters = {}
    for cluster_id in sorted(cluster_df['cluster'].unique()):
        if cluster_id >= 0:  # Exclude noise points (-1) from DBSCAN
            clusters[cluster_id] = cluster_df[cluster_df['cluster'] == cluster_id]['ADM3_EN'].tolist()
            print(f"\nCluster {cluster_id}: {len(clusters[cluster_id])} regions")
            print(f"  Sample regions: {clusters[cluster_id][:5]}")
    
    # Calculate pairwise similarity (correlation) matrix
    correlation_matrix = np.corrcoef(X_scaled)
    similarity_df = pd.DataFrame(
        correlation_matrix,
        index=combined_features.index,
        columns=combined_features.index
    )
    
    return clusters, cluster_df, similarity_df, combined_features
