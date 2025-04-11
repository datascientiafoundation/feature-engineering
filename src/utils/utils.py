import logging
import os
import sys
import pandas as pd
import random

# =============================== UTILS FOR FEATURE ENGINEERING =======================

from math import sin, cos, atan2, sqrt, pi
import numpy as np
from geopy.distance import great_circle
from shapely.geometry import MultiPoint

# earth's mean radius = 6,371km
earthradius = 6371.0


def centermost_point(cluster):
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
    centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)
    return centermost_point  # ['latitude', 'longitude'])


def getDistanceByHaversine(loc1, loc2):
    # source https://github.com/scikit-mobility/scikit-mobility/blob/e9c32bd1ca51d7fe691ed05db59483e87654a164/skmob/utils/gislib.py#L31
    "Haversine formula - give coordinates as (lat_decimal,lon_decimal) tuples"

    lat1, lon1 = loc1
    lat2, lon2 = loc2

    # convert to radians
    lon1 = lon1 * pi / 180.0
    lon2 = lon2 * pi / 180.0
    lat1 = lat1 * pi / 180.0
    lat2 = lat2 * pi / 180.0

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (sin(dlat / 2)) ** 2 + cos(lat1) * cos(lat2) * (sin(dlon / 2.0)) ** 2
    c = 2.0 * atan2(sqrt(a), sqrt(1.0 - a))
    km = earthradius * c
    return km


def radius_of_gyration(x):
    # source https://github.com/scikit-mobility/scikit-mobility/blob/e9c32bd1ca51d7fe691ed05db59483e87654a164/skmob/measures/individual.py#L12
    lats_lngs = x[['latitude', 'longitude']].values
    center_of_mass = np.mean(lats_lngs, axis=0)
    rg = np.sqrt(np.mean([getDistanceByHaversine((lat, lng), center_of_mass) ** 2.0 for lat, lng in lats_lngs]))
    return rg


def get_total_distance_covered(x):
    # [source](https://github.com/scikit-mobility/scikit-mobility/blob/e9c32bd1ca51d7fe691ed05db59483e87654a164/skmob/measures/individual.py#L465)
    lats_lngs = x.sort_values(by='timestamp')[['latitude', 'longitude']].values
    lengths = np.array([getDistanceByHaversine(lats_lngs[i], lats_lngs[i - 1]) for i in range(1, len(lats_lngs))])
    return np.sum(lengths)


def set_seed(seed=42):
    """
    Sets the random seed for various libraries for reproducibility.
    """
    random.seed(seed)
    np.random.seed(seed)

###

def _intervalindex_to_columns(df):
    df[['start_interval', 'end_interval']] = df.apply(
        func=lambda row: [row['interval'].left, row['interval'].right],
        result_type='expand',
        axis=1)
    df.pop('interval')


def parse_interval(df):
    return df.apply(
        lambda row: pd.Interval(row['start_interval'], row['end_interval'], closed='left'), axis=1)


def get_logger(name, filename, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    file_handler = logging.FileHandler(filename=filename, mode='w')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger
