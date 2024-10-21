# Authenticate and initialize Earth Engine
import ee
ee.Authenticate()
ee.Initialize()
import geemap
import pandas as pd
from datetime import datetime, timedelta


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
        scale=500,  # Native resolution of Sentinel-5P is ~7 km
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

import geopandas as gpd

ethiopia = gpd.read_file("data/boundaries/eth_admbnda_adm1_csa_bofedb_2021.shp")
addis = ethiopia[ethiopia['ADM1_EN']=='Addis Ababa']
tigray = ethiopia[ethiopia['ADM1_EN']=='Tigray']

ethiopia_adm0 = gpd.read_file('data/boundaries/eth_admbnda_adm0_csa_bofedb_itos_2021.shp')

start_date = '2023-01-01'
end_date = '2023-12-31'

aoi = geemap.geopandas_to_ee(addis)

process_no2_data_for_aoi_to_file(aoi, start_date, end_date, 'addis_500m')