# Authenticate and initialize Earth Engine
import ee
ee.Authenticate()
ee.Initialize()
import geemap
import pandas as pd
from datetime import datetime, timedelta

def calculate_monthly_no2_at_native_resolution(year, month, aoi, NO2Collection):
    """
    Calculate the monthly average NO2 values at the native resolution.
    """
    # Define the start and end dates for the given month
    start_date = ee.Date(f"{year}-{month:02d}-01")
    end_date = start_date.advance(1, 'month')

    # Filter NO2 data for the entire month
    filtered_month = NO2Collection.filterDate(start_date, end_date)
    
    # Calculate the mean NO2 for the entire month
    monthly_mean = filtered_month.mean()

    # Sample the image at native resolution to get pixel geometry and NO2 values
    sampled_pixels = monthly_mean.sample(
        region=aoi,
        scale=1000,  # Native resolution of Sentinel-5P is ~7 km, adjust if needed
        projection='EPSG:4326',  # Ensure the output is in lat/lon
        geometries=True  # Include pixel geometries (lat/lon)
    )

    # Add month and year to each sampled pixel
    def add_month_year(feature):
        return feature.set({
            'year': year,
            'month': month
        })

    sampled_pixels_with_date = sampled_pixels.map(add_month_year)
    
    return sampled_pixels_with_date



def calculate_daily_no2_for_single_day_by_admin_region(start_date, admin_regions, NO2Collection):
    # Define the start and end date for a single day
    start_date = ee.Date(start_date)
    end_date = start_date.advance(1, 'day')
    
    # Filter NO2 data for the single day
    filtered_day = NO2Collection.filterDate(start_date, end_date)
    
    # Calculate mean NO2 for the day (note: no averaging over multiple days, just this day)
    daily_mean = filtered_day.mean()

    # Calculate the mean NO2 value over each administrative region
    zonal_mean = daily_mean.reduceRegions(
        collection=admin_regions,  # Administrative regions to calculate zonal statistics
        reducer=ee.Reducer.mean(),  # Use mean reducer to compute average NO2 per region
        scale=1000,  # Approximate resolution of Sentinel-5P NO2 data
        crs='EPSG:4326'  # Coordinate reference system
    )
    
    return zonal_mean

def remove_geometry(feature):
    """Remove the geometry from the feature."""
    return feature.setGeometry(None)

def calculate_monthly_no2_by_admin_region(year, month, admin_regions, NO2Collection):
    # Define the start and end date for the given month
    start_date = ee.Date(f"{year}-{month:02d}-01")
    end_date = start_date.advance(1, 'month')

    # Filter NO2 data for the entire month
    filtered_month = NO2Collection.filterDate(start_date, end_date)
    
    # Calculate mean NO2 for the entire month
    monthly_mean = filtered_month.mean()

    # Calculate the mean NO2 value over each administrative region
    zonal_mean = monthly_mean.reduceRegions(
        collection=admin_regions,  # Administrative regions to calculate zonal statistics
        reducer=ee.Reducer.mean(),  # Use mean reducer to compute average NO2 per region
        scale=1000,  # Approximate resolution of Sentinel-5P NO2 data
        crs='EPSG:4326'  # Coordinate reference system
    )

    # Remove geometry from each feature
    zonal_mean_without_geom = zonal_mean.map(remove_geometry).select(['mean'])  # Include only the property fields

    return zonal_mean_without_geom





def calculate_daily_no2_for_day_time(start_date):
    # Define the start and end time for 8 AM to 6 PM
    start_date = ee.Date(start_date)
    end_date = start_date.advance(1, 'day')

    # Filter NO2 data for the single day and within the time range 8 AM to 6 PM
    filtered_day = NO2Collection.filterDate(start_date, end_date) \
        .filter(ee.Filter.calendarRange(8, 18, 'hour'))  # Filter for the hours 8 AM to 6 PM

    # Calculate mean NO2 for the day within the specified time range
    daily_mean = filtered_day.mean()

    # Sample the image at native resolution to get pixel geometry and NO2 values
    sampled_pixels = daily_mean.sample(
        region=aoi,
        scale=1000,  # Native resolution of Sentinel-5P is ~7 km
        projection='EPSG:4326',  # Ensure the output is in lat/lon
        geometries=True  # Include pixel geometries (lat/lon)
    )

def calculate_daily_no2_for_single_day(start_date, aoi, NO2Collection):
    start_date = ee.Date(start_date)
    end_date = start_date.advance(1, 'day')
    
    # Filter NO2 data for the single day
    filtered_day = NO2Collection.filterDate(start_date, end_date)
    
    # Calculate mean NO2 for the day (note: no averaging over multiple days, just this day)
    daily_mean = filtered_day.mean()

    # Sample the image at native resolution to get pixel geometry and NO2 values
    sampled_pixels = daily_mean.sample(
        region=aoi,
        scale=1000,  # Native resolution of Sentinel-5P is ~7 km
        projection='EPSG:4326',  # Ensure the output is in lat/lon
        geometries=True  # Include pixel geometries (lat/lon)
    )

    
    def add_date(feature):
        return feature.set('date', start_date.format('YYYY-MM-dd'))
    
    sampled_pixels_with_date = sampled_pixels.map(add_date)
    
    return sampled_pixels_with_date

def calculate_monthly_no2_for_single_month(year, month, aoi, NO2Collection):
    # Define the start and end dates for the given month
    start_date = ee.Date(f"{year}-{month:02d}-01")
    end_date = start_date.advance(1, 'month')

    # Filter NO2 data for the entire month
    filtered_month = NO2Collection.filterDate(start_date, end_date)
    
    # Calculate mean NO2 for the entire month
    monthly_mean = filtered_month.mean()

    # Sample the image at native resolution to get pixel geometry and NO2 values
    sampled_pixels = monthly_mean.sample(
        region=aoi,
        scale=1000,  # Native resolution of Sentinel-5P is ~7 km
        projection='EPSG:4326',  # Ensure the output is in lat/lon
        geometries=False  # Include pixel geometries (lat/lon)
    )

    return sampled_pixels

# Split the date range into 10-day chunks
def split_dates_into_chunks(start_date, end_date, chunk_size=10):
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')

    current = start
    chunks = []

    while current < end:
        next_chunk = current + timedelta(days=chunk_size)
        chunks.append((current.strftime('%Y-%m-%d'), min(next_chunk, end).strftime('%Y-%m-%d')))
        current = next_chunk
    
    return chunks

import time

# Initialize an empty DataFrame to store the final results

def process_no2_data_for_aoi_to_drive(aoi, aoi_name, start_date, end_date):
    # Load NO2 ImageCollection
    NO2Collection = ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_NO2").select('NO2_column_number_density')

    # Create an empty FeatureCollection to accumulate all the days
    final_collection = ee.FeatureCollection([])

    # Split the date range into 10-day chunks
    date_chunks = split_dates_into_chunks(start_date, end_date)

    # Loop through each 10-day chunk and process data
    for chunk_start_date, chunk_end_date in date_chunks:
        print(f"Processing data from {chunk_start_date} to {chunk_end_date}...")

        # Loop through each day in this 10-day chunk
        current_date = datetime.strptime(chunk_start_date, '%Y-%m-%d')
        end_date_dt = datetime.strptime(chunk_end_date, '%Y-%m-%d')

        while current_date <= end_date_dt:
            # Convert current date to string format
            current_date_str = current_date.strftime('%Y-%m-%d')
            
            # Calculate NO2 for this specific day
            sampled_pixels_with_date = calculate_daily_no2_for_single_day(current_date_str, aoi, NO2Collection)

            # Add this day's data to the final collection
            final_collection = final_collection.merge(sampled_pixels_with_date)

            # Move to the next day
            current_date += timedelta(days=1)

    # Now export the entire final collection as a single CSV file
    output_file = f'no2_{aoi_name}_{start_date.replace("-", "")}_{end_date.replace("-", "")}.csv'

    # Export the data to Google Drive as a single CSV file
    export_task = ee.batch.Export.table.toDrive(
        collection=final_collection,
        description=f"NO2_sample_{aoi_name}_{start_date}_to_{end_date}",
        folder="EarthEngineExports",  # The folder in Google Drive where the file will be saved
        fileNamePrefix=output_file.replace('.csv', ''),  # Remove '.csv' since Earth Engine adds it automatically
        fileFormat="CSV"
    )
    export_task.start()

    while export_task.active():
        print('Exporting... Task status:', export_task.status()['state'])
        time.sleep(30)  # Wait for 30 seconds before checking again

    # Check the final status
    status = export_task.status()
    if status['state'] == 'COMPLETED':
        print(f"Export completed successfully: {output_file}")
    else:
        print(f"Export failed: {status}")

def process_no2_data_for_aoi_to_gcs(aoi, aoi_name, start_date, end_date, gcs_bucket, admin_regions=None):
    # Load NO2 ImageCollection
    NO2Collection = ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_NO2").select('NO2_column_number_density')

    # Split the date range into 10-day chunks
    date_chunks = split_dates_into_chunks(start_date, end_date)

    # Loop through each 10-day chunk and process data
    for chunk_start_date, chunk_end_date in date_chunks:
        print(f"Processing data from {chunk_start_date} to {chunk_end_date}...")

        # Loop through each day in this 10-day chunk
        current_date = datetime.strptime(chunk_start_date, '%Y-%m-%d')
        end_date_dt = datetime.strptime(chunk_end_date, '%Y-%m-%d')

        while current_date <= end_date_dt:
            # Convert current date to string format
            current_date_str = current_date.strftime('%Y-%m-%d')

            if admin_regions is not None:
                # Calculate NO2 for this specific day by admin region
                sampled_pixels_with_date = calculate_daily_no2_for_single_day_by_admin_region(current_date_str, admin_regions, NO2Collection)
            else:
                # Calculate NO2 for this specific day by native resolution
                sampled_pixels_with_date = calculate_daily_no2_for_single_day(current_date_str, aoi, NO2Collection)

            # Define the output CSV file name with a partition based on date
            output_file = f"no2_{aoi_name}/{current_date_str.replace('-', '')}.csv"

            # Export the data to Google Cloud Storage as CSV
            export_task = ee.batch.Export.table.toCloudStorage(
                collection=sampled_pixels_with_date,
                description=f"NO2_sample_{aoi_name}_{current_date_str}",
                bucket=gcs_bucket,
                fileNamePrefix=output_file.replace('.csv', ''),  # Remove '.csv' since Earth Engine adds it automatically
                fileFormat="CSV"
            )
            export_task.start()

            while export_task.active():
                print(f'Exporting data for {current_date_str}... Task status:', export_task.status()['state'])
                time.sleep(30)  # Wait for 30 seconds before checking again

            # Check the final status
            status = export_task.status()
            if status['state'] == 'COMPLETED':
                print(f"Export completed successfully for {current_date_str} to Google Cloud Storage: {output_file}")
            else:
                print(f"Export failed for {current_date_str}: {status}")

            # Move to the next day
            current_date += timedelta(days=1)

def process_monthly_no2_data_for_aoi_to_gcs(aoi, aoi_name, start_date, end_date, gcs_bucket, admin_regions=None):
    # Load NO2 ImageCollection
    NO2Collection = ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_NO2").select('NO2_column_number_density')

    # Convert start_date and end_date to datetime objects
    start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')

    # Generate a list of (year, month) tuples within the specified range
    months = []
    current_date = start_date_dt
    while current_date <= end_date_dt:
        months.append((current_date.year, current_date.month))
        # Move to the start of the next month
        current_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)

    # Create an empty FeatureCollection to accumulate the monthly data
    final_collection = ee.FeatureCollection([])

    # Loop through each month and process data
    for year, month in months:
        print(f"Processing data for {year}-{month:02d}...")

        if admin_regions is not None:
            # Calculate NO2 for this specific month by admin region
            sampled_pixels_with_date = calculate_monthly_no2_by_admin_region(year, month, admin_regions, NO2Collection)
        else:
            # Calculate NO2 for this specific month by native resolution
            sampled_pixels_with_date = calculate_monthly_no2_for_single_month(year, month, aoi, NO2Collection)

        date_str = f"{year}-{month:02d}-01"
        def add_date(feature):
            return feature.set('date', date_str)

        sampled_pixels_with_date = sampled_pixels_with_date.map(add_date)

        # Merge this month's results into the final collection
        final_collection = final_collection.merge(sampled_pixels_with_date)

    # Define the output CSV file name for the entire range
    output_file = f"no2_{aoi_name}_{start_date.replace('-', '')}_{end_date.replace('-', '')}.csv"

    # Export the final collection to Google Cloud Storage as a single CSV file
    export_task = ee.batch.Export.table.toCloudStorage(
        collection=final_collection,
        description=f"NO2_sample_{aoi_name}_{start_date}_to_{end_date}",
        bucket=gcs_bucket,
        fileNamePrefix=output_file.replace('.csv', ''),  # Remove '.csv' since Earth Engine adds it automatically
        fileFormat="CSV"
    )
    export_task.start()

    while export_task.active():
        print('Exporting... Task status:', export_task.status()['state'])
        time.sleep(30)  # Wait for 30 seconds before checking again

    # Check the final status
    status = export_task.status()
    if status['state'] == 'COMPLETED':
        print(f"Export completed successfully to Google Cloud Storage: {output_file}")
    else:
        print(f"Export failed: {status}")




def process_no2_data_for_aoi_to_file(aoi, start_date, end_date, aoi_name):
    # Load NO2 ImageCollection

    NO2Collection = ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_NO2") \
        .select('NO2_column_number_density')

    final_df = pd.DataFrame()

    date_chunks = split_dates_into_chunks(start_date, end_date)

    # Loop through each 10-day chunk and process data
    for chunk_start_date, chunk_end_date in date_chunks:
        print(f"Processing data from {chunk_start_date} to {chunk_end_date}...")

        # Loop through each day in this 10-day chunk
        current_date = datetime.strptime(chunk_start_date, '%Y-%m-%d')
        end_date_dt = datetime.strptime(chunk_end_date, '%Y-%m-%d')

        while current_date <= end_date_dt:
            # Convert current date to string format
            current_date_str = current_date.strftime('%Y-%m-%d')
            
            # Calculate NO2 for this specific day
            sampled_pixels_with_date = calculate_daily_no2_for_single_day(current_date_str, aoi, NO2Collection)

            # Get the results as a Python dictionary and convert it to a DataFrame
            data = sampled_pixels_with_date.getInfo()
            features = data['features']

            # Extract the NO2, date, and coordinates for each pixel
            records = []
            for feature in features:
                props = feature['properties']
                coords = feature['geometry']['coordinates']
                records.append({
                    'date': props['date'],
                    'NO2': props['NO2_column_number_density'],
                    'longitude': coords[0],
                    'latitude': coords[1]
                })

            # Convert the list of records to a DataFrame
            df = pd.DataFrame(records)
            
            # Concatenate the results into the final DataFrame
            final_df = pd.concat([final_df, df], ignore_index=True)
            
            # Move to the next day
            current_date += timedelta(days=1)

    # Write final DataFrame to CSV file using the original start and end dates
    output_file = f'./data/air_pollution/no2_{aoi_name}_{start_date.replace("-","")}_{end_date.replace("-","")}.csv'
    final_df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")

# Loop through each month and calculate the native resolution monthly average
def process_monthly_no2_at_native_resolution(aoi, start_date, end_date, gcs_bucket, aoi_name):
    # Load NO2 ImageCollection
    NO2Collection = ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_NO2").select('NO2_column_number_density')

    # Convert start_date and end_date to datetime objects
    start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')

    # Generate a list of (year, month) tuples within the specified range
    months = []
    current_date = start_date_dt
    while current_date <= end_date_dt:
        months.append((current_date.year, current_date.month))
        # Move to the start of the next month
        current_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)

    # Create an empty FeatureCollection to accumulate the monthly data at native resolution
    final_collection = ee.FeatureCollection([])

    # Loop through each month and process data at native resolution
    for year, month in months:
        print(f"Processing data at native resolution for {year}-{month:02d}...")

        # Calculate NO2 for this specific month at native resolution
        sampled_pixels = calculate_monthly_no2_at_native_resolution(year, month, aoi, NO2Collection)

        # Merge this month's results into the final collection
        final_collection = final_collection.merge(sampled_pixels)

    # Define the output CSV file name for the entire range
    output_file = f"no2_native_{aoi_name}_{start_date.replace('-', '')}_{end_date.replace('-', '')}.csv"

    # Export the final collection to Google Cloud Storage as a single CSV file
    export_task = ee.batch.Export.table.toCloudStorage(
        collection=final_collection,
        description=f"NO2_sample_{aoi_name}_native_{start_date}_to_{end_date}",
        bucket=gcs_bucket,
        fileNamePrefix=output_file.replace('.csv', ''),  # Remove '.csv' since Earth Engine adds it automatically
        fileFormat="CSV"
    )
    export_task.start()

    while export_task.active():
        print('Exporting native resolution data... Task status:', export_task.status()['state'])
        time.sleep(30)  # Wait for 30 seconds before checking again

    # Check the final status
    status = export_task.status()
    if status['state'] == 'COMPLETED':
        print(f"Export completed successfully to Google Cloud Storage: {output_file}")
    else:
        print(f"Export failed: {status}")


import geopandas as gpd

ethiopia = gpd.read_file("data/boundaries/eth_admbnda_adm1_csa_bofedb_2021.shp")
addis = ethiopia[ethiopia['ADM1_EN']=='Addis Ababa']
tigray = ethiopia[ethiopia['ADM1_EN']=='Tigray']

ethiopia_adm0 = gpd.read_file('data/boundaries/eth_admbnda_adm0_csa_bofedb_itos_2021.shp')
ethiopia_adm1 = gpd.read_file('data/boundaries/eth_admbnda_adm1_csa_bofedb_2021.shp')
ethiopia_adm3 = gpd.read_file('data/boundaries/eth_admbnda_adm3_csa_bofedb_2021.shp')
djibouti_addis = gpd.read_file('data/boundaries/ethiopia_adm3_djibouti_addis_outline.shp')

admin_regions_ee = geemap.geopandas_to_ee(djibouti_addis)

start_date = '2024-05-11'
end_date = '2024-05-12'


aoi = geemap.geopandas_to_ee(djibouti_addis)

process_no2_data_for_aoi_to_gcs(
    aoi=aoi,
    aoi_name='djibouti_addis',
    start_date=start_date,
    end_date=end_date,
    gcs_bucket='datalab-air-pollution'
)