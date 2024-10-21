"""
Module with miscellaneous functions for geospatial data processing
Created on Mar 6, 2023
@author-1: Dunstan Matekenya
@author-2: Andres

For the sake of convinience and to reduce dependencies, some functions have 
been copied from the following repos/packages:
1. GOSTnets
2. https://github.com/worldbank/INFRA_SAP/blob/master/infrasap/market_access.py
"""
import os
from pathlib import Path
import shutil
import zipfile
from datetime import datetime
import json
import requests
import math
from rasterstats import gen_point_query, gen_zonal_stats
import rasterio
from rasterio.crs import CRS
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.mask import mask

import skimage.graph as graph
os.environ["USE_PYGEOS"] = "0"
import geopandas as gpd
import pandas as pd
import numpy as np

from shapely.geometry import shape
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info
import boto3
from botocore import UNSIGNED
from botocore.config import Config

from math import asin, atan2, cos, degrees, radians, sin



def get_bounding_box(shapefile_or_gdf):
    """
    Generates the bounding box with min and max latitude and longitude for a given shapefile or GeoDataFrame.

    Parameters:
    shapefile_or_gdf (str or GeoDataFrame): The path to the shapefile or a GeoDataFrame.

    Returns:
    dict: A dictionary with the min/max latitude and longitude.
    """
    # Check if input is a file path (str) or a GeoDataFrame
    if isinstance(shapefile_or_gdf, str):
        # Load the shapefile using geopandas if a file path is provided
        gdf = gpd.read_file(shapefile_or_gdf)
    elif isinstance(shapefile_or_gdf, gpd.GeoDataFrame):
        # Use the provided GeoDataFrame
        gdf = shapefile_or_gdf
    else:
        raise ValueError("Input must be a file path (str) or a GeoDataFrame.")

    # Get the bounds of the shapefile geometry
    bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
    
    # Extract the bounding box values
    bounding_box = {
        'min_longitude': bounds[0],  # min x (longitude)
        'min_latitude': bounds[1],   # min y (latitude)
        'max_longitude': bounds[2],  # max x (longitude)
        'max_latitude': bounds[3]    # max y (latitude)
    }
    
    return bounding_box

def convert_wgs_coordinates_to_utm(lon, lat):
    """
    Given latitude, longitude coordinates based on WGS84, convert to
    UTM zone and EPSG code. Shamelessly copied from here:
    https://stackoverflow.com/questions/40132542/
    Parameters
    ----------
    lon - input longitude
    lat - input latitude

    Returns EPSG code
    -------

    """
    utm_band = str((math.floor((lon + 180) / 6) % 60) + 1)
    if len(utm_band) == 1:
        utm_band = '0' + utm_band
    if lat >= 0:
        epsg_code = '326' + utm_band
    else:
        epsg_code = '327' + utm_band
    return epsg_code


def utm_zones_from_geodataframe(gdf, datum='WGS 84', return_zones=False):
    """
    Returns estimated UTM CRS from the geopandas dataframe
    Parameters
    ----------
    gdf: gpd.GeoDataframe: Geopandas dataframe
    return_zones: Boolean : Whether to return UTM zones or EPSG code.

    Returns
    -------

    """

    # get layer bounds
    min_lon, min_lat, max_lon, max_lat = gdf.total_bounds

    utm_crs_list = query_utm_crs_info(
        datum_name=datum,
        area_of_interest=AreaOfInterest(
            west_lon_degree=min_lon,
            south_lat_degree=min_lat,
            east_lon_degree=max_lon,
            north_lat_degree=max_lat,
        ),
    )
    utm_crs_code_list = [i[1] for i in utm_crs_list]
    if return_zones:
        return [i[-2:] for i in utm_crs_code_list]
    else:
        return utm_crs_code_list


def distance_between_points(pt1=None, pt2=None):
    """
    Calculate the Haversine distance betweeen 2 points.

    Parameters
    ----------
    pt1 : tuple of float
        (lat, long)
    pt2 : tuple of float
        (lat, long)

    Returns
    -------
    distance_in_km : float

    Examples
    --------
    >>> pt1 = (48.1372, 11.5756)  # Munich
    >>> pt2 = (52.5186, 13.4083)  # Berlin
    >>> round(distance_between_points(pt1, pt2), 1)
    504.2
    """
    lat1, lon1 = pt1
    lat2, lon2 = pt2
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d


def distance_matrix(xy_list=None):
    """
    Return distance matrix from a dictlist of xy coordinates
    :param xy_list:
    :return: a dataframe style of distance matrix
    """
    df = pd.DataFrame([dict(d._asdict()) for d in xy_list])

    for pt in xy_list:
        pt_id = pt.point_id
        colname = 'to_' + str(pt_id)
        df[colname] = df.apply(lambda x: distance_between_points(
            pt1=(x['x'], x['y']), pt2=(pt.x, pt.y)), axis=1)

    return df


def distance_to_points(dest_pts, target_pt, lon_col='lon', lat_col='lat', 
                       id_col='id', output='nearest'):
    """
    Measure distance from target_pt to all points in dest_pts.
    Parameters
    ----------
    dest_pts - Either a list or a Pandas Dataframe. If a list, it should be a lilike this:  [(lat,lon)] or [(lat,lon,id)]
    target_pt(tuple) - A target point to measure distance from provided as a (lat,lon)
    lon_col(str) - Column with longitude values
    lat_col(str) - Column with latitude values
    id_col (str) - Column with row id if interested in returning nearest point id
    output - nearest-output distance to nearest point; nearest_id-output id of nearest point; dist_list-output distance list.

    Returns A list containing floats
    -------
    """
    if isinstance(dest_pts, pd.DataFrame):
        df = dest_pts.copy(deep=True)
    else:
        if len(dest_pts[0]) == 3:
            df = pd.DataFrame(dest_pts, columns=[lat_col, lon_col, id_col])
        else:
            df = pd.DataFrame(dest_pts, columns=[lat_col, lon_col])
    df['dist'] = df.apply(lambda x: distance_between_points(pt1=(x[lat_col], x[lon_col]),
                                                            pt2=(target_pt[0], target_pt[1])), axis=1)
    if output == 'nearest':
        return df['dist'].min()
    elif output == 'nearest_id':
        try:
            return df.sort_values(by='dist',ascending=True).iloc[0][id_col]
        except:
            print('Make sure you provided ID column')
    elif output == 'dist_list':
        return list(df['dist'].values)
    else:
        return list(df['dist'].values)


def load_csv_into_geopandas(csv_with_coords, lat, lon):
    """
    Helper function to convert a CSV file with lat, lon into Geopandas Geodataframe

    Parameters
    ----------
    csv_with_coords(str) - Full path of CSV file with coordinates
    lat(str) - Column name with latitude
    lon(str) - Column name with longitude

    Returns
    -------
    A Geopandas GeoDataframe
    """
    df = pd.read_csv(csv_with_coords)
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df[lon], df[lat]), crs=4326)

    return gdf


def clip_raster(input_raster, clip_polygon, out_file):
    ''' 
    Clip input raster using shapefile copied from:
    https://github.com/worldbank/GOST/blob/Scripts/GOSTRocks/rasterMisc.py

    Parameters
    ----------
    input_raster(rasterio object) - Raster file to clip
    clip_polygon (Geopandas object) -  Polygon of extents to clip to
    out_file (str) - Full path with extension of output clipped TIF

    Returns
    -------
    Saves TIF file to provided path (out_file)
    '''
    if clip_polygon.crs != input_raster.crs:
        clip_polygon = clip_polygon.to_crs(input_raster.crs)
    out_meta = input_raster.meta.copy()

    def getFeatures(gdf):
        # Function to parse features from GeoDataFrame in such a manner that rasterio wants them
        return [json.loads(gdf.to_json())['features'][0]['geometry']]
    tD = gpd.GeoDataFrame([[1]], geometry=[clip_polygon.unary_union])
    coords = getFeatures(tD)
    out_img, out_transform = mask(input_raster, shapes=coords, crop=True)
    out_meta.update({"driver": "GTiff",
                     "height": out_img.shape[1],
                     "width": out_img.shape[2],
                     "transform": out_transform})
    with rasterio.open(out_file, "w", **out_meta) as dest:
        dest.write(out_img)


def get_geoboundaries_adm_layer(co_iso='MWI', admin_level=0, release_type="gbOpen"):
    """
    Retrieves admin boundaries for country from https://www.geoboundaries.org/api.html API.

    Parameters
    ----------
    co_iso(str) - Country ISO3 code, for example MWI
    admin_level(int) - Admin level provided as an integer

    Returns
    -------
    A Geopandas GeoDataframe
    """

    assert len(co_iso) == 3, 'PLEASE PROVIDE A VALID ISO CODE FOR THE COUNTRY'
    assert admin_level < 10, 'PLEASE PROVIDE A VALID ADMIN LEVEL NUMBER'

    # ==========================================
    # LOAD GEOBOUNDARY JSON OBJECT
    # ==========================================
    base_url = "https://www.geoboundaries.org/api/current/"
    admin_lev_str = f"ADM{admin_level}"
    target_url = f"{base_url}/{release_type}/{co_iso}/{admin_lev_str.lower()}/"
    r = requests.get()
    dl_path = r.json()[0]['gjDownloadURL']
    geom_json = requests.get(dl_path).json()

    return 

    # ==========================================
    # CONVERT JSON INTO GEOPANDAS DATAFRAME
    # ==========================================
    # For now just extract WGS84
    # Also, just default to WGS84
    # TO-DO: find a better way to convert from OGC CRS to EPSG
    try:
        crs_name = geom_json['crs']['properties']['name'].split(":")[-1]
        if crs_name == 'CRS84':
            crs_epsg_code = 4326
        else:
            crs_epsg_code = 4326
            print('Please manually check CRS, now defaulting to WGS-84')
    except:
        print('Please manually check CRS, now defaulting to WGS-84')
        crs_epsg_code = 4326

    data = []
    for feature in geom_json['features']:
        properties = feature['properties']
        geometry = shape(feature['geometry'])
        properties['geometry'] = geometry
        data.append(properties)

    gdf = gpd.GeoDataFrame(data, crs=crs_epsg_code)

    return gdf


def terminal_coordinates(origin_coords, bearing, distance, return_degrees=True):
    """Calculates end coordinates in decimal degrees given initial/origin coordinates in decimal degrees.

    Parameters
    ----------
    origin_coords : tuple
        Initial coordinates in decimal degrees given as a lon,lat tuple.
    bearing : float
        Bearings or azimuths (in degrees) start with 0 degrees toward true north, 90 degrees east, 
        180 degrees south, and 270 degrees west (clockwise rotation)
    distance : int
        Distance in meters.
    return_degrees : Boolean, default = True
        Whether to return new point in degrees or meters

    Returns
    ----------
    Tuple
        New coordinates as a (lon,lat) tuple
    """
    # ==========================
    # DO CONVERSIONS
    # ==========================
    # Convert the angle from degrees to radians
    angle_radian = bearing * (math.pi / 180)

    # Convert decimal degrees to meters
    x, y = pod.degrees_to_meters(origin_coords[0], origin_coords[1])

    # get projected CRS EPSG code
    utm_crs_epsg = int(convert_wgs_coordinates_to_utm(
        origin_coords[0], origin_coords[1]))

    # ==========================
    # GENERATE NEW POINT
    # ==========================
    # Generate the offset by applying trig formulas (law of cosines) using the distance as
    # the hypotenuse solving for the other sides
    x_offset = math.sin(angle_radian) * distance
    y_offset = math.cos(angle_radian) * distance

    # Add the offset to the original coordinates (in meters)
    x_new = x + x_offset
    y_new = y + y_offset

    # Convert back to degrees
    if return_degrees:
        x_degrees, y_degrees = pod.meters_to_degrees(
            x_new, y_new, utm_crs_epsg=utm_crs_epsg)
        return x_degrees, y_degrees
    else:
        return x_new, y_new


def terminal_coordinates_faster(lat1, lon1, d, bearing, R=6371):
    """
    lat: initial latitude, in degrees
    lon: initial longitude, in degrees
    d: target distance from initial
    bearing: (true) heading in degrees
    R: optional radius of sphere, defaults to mean radius of earth

    Returns new lat/lon coordinate {d}km from initial, in degrees
    """
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    a = radians(bearing)
    lat2 = asin(sin(lat1) * cos(d/R) + cos(lat1) * sin(d/R) * cos(a))
    lon2 = lon1 + atan2(
        sin(a) * sin(d/R) * cos(lat1),
        cos(d/R) - sin(lat1) * sin(lat2)
    )
    return degrees(lon2), degrees(lat2)


def download_osm_shapefiles(region, country, outdir):
    """Downloads OSM latest shapefile from http://download.geofabrik.de/

    Parameters
    ----------
    region : str
        Continent/region where country is located as used on Geofrabrik website. For example, Africa, Asia, 
        South America (south-america)
    country : str
        Country name in full _description_
    outdir : str
        Directory to save the data.

    Returns
    --------
    Saves and unzips downloaded files in directory: outdir + country-latest-free-shp
    """
    start = datetime.now()
    geofabrick_url = 'http://download.geofabrik.de/{}/{}-latest-free.shp.zip'.format(
        region.lower(), country.lower())
    r = requests.get(geofabrick_url, allow_redirects=True)
    try:
        assert r.status_code == 200
    except AssertionError:
        print('ENSURE THERE IS INTERNET AND/OR REGION AND COUNTRY NAMES ARE CORRECT')
        return

    assert outdir.exists(), 'ENSURE OUTPUT DIRECTORY EXISTS'
    outfile = Path(outdir).joinpath(geofabrick_url.split("/")[-1])
    print('Saving file .............')
    open(outfile, 'wb').write(r.content)

    print()
    print('Unzipping file .............')
    extract_outdir = Path(outdir).joinpath(
        outfile.parts[-1].split(".")[0] + "-shp").mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(outfile, "r") as zip_ref:
        zip_ref.extractall(extract_outdir)

    # Delete zipfile
    file_size = outfile .stat()[6]/1000000
    shutil.rmtree(outfile)

    end = datetime.now()
    time_taken = (end - start).total_seconds/60

    print()
    print('Downloading {} MB took {} minutes'.format(
        int(file_size)), int(time_taken))

    return extract_outdir


def reproject_tif(in_tif, out_tif, dst_crs='EPSG:4326'):
    """Use rasterio to reproject raster.

    Parameters
    ----------
    in_tif : str
        Full path to input raster (tif)
    out_tif : str
        Full path to output raster (tif)
    dst_crs : str, optional
        Destination CRS in EPSG format
    """
    with rasterio.open(in_tif) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        with rasterio.open(out_tif, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)


def tif_from_other(in_tif, out_tif, dst_crs='EPSG:4326'):
    """Use rasterio to save as TIF from other formats

    Parameters
    ----------
    in_tif : str
        Full path to input raster (tif)
    out_tif : str
        Full path to output raster (tif)
    dst_crs : str, optional
        Destination CRS in EPSG format
    """
    with rasterio.open(in_tif) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        with rasterio.open(out_tif, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)




