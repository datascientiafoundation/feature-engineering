"""
Generate the final data set used by SKEL
"""
import os.path
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

from src.config import sensors_config
from src.utils.utils import get_logger, _intervalindex_to_columns, parse_interval


# Some userful references:
# https://developers.google.com/machine-learning/crash-course/representation/qualities-of-good-features

def is_weekday(day):
    return day not in [5, 6]


def determine_day_period(hour) -> str:
    if 6 <= hour < 10:
        return "morning"
    if 10 <= hour < 14:
        return "noon"
    if 14 <= hour < 18:
        return "afternoon"
    if 18 <= hour < 22:
        return "evening"
    else:
        return "night"


def discretize_rssi(value) -> str:
    # info https://www.metageek.com/training/resources/understanding-rssi/
    values = [-40, -67, -80, -90]
    values = values * -1
    pd.cut(values, bins=[0, 50, 70, 90, np.inf], labels=['good', 'medium', 'bad', 'unusable'], right=True)


def get_x(path_to_sensors) -> pd.DataFrame:
    features_union = None
    for sensor_path in path_to_sensors:
        logger.info(f'load {sensor_path.name}')
        sensors = pd.read_csv(
            sensor_path,
            parse_dates=['start_interval', 'end_interval']
        )
        columns_to_exclude = sensors_config.get(sensor_path.stem, {}).get('columns_to_exclude')
        logger.info(f'exclude columns {columns_to_exclude}')
        if columns_to_exclude:
            sensors.drop(columns_to_exclude, inplace=True)
        types_dict = {'userid': int, 'experimentid': str}
        for col, col_type in types_dict.items():
            sensors[col] = sensors[col].astype(col_type)

        sensors['interval'] = parse_interval(sensors)
        sensors.drop(['start_interval', 'end_interval'], axis=1, inplace=True)
        sensors.set_index(['userid', 'experimentid', 'interval'], inplace=True)

        if features_union is None:
            features_union = sensors
        else:
            features_union = features_union.join(sensors, how='outer', validate="one_to_one")

    # assert all(features_union[['latitude', 'longitude']].nona())
    intervals = pd.Series(features_union.index.get_level_values(2))
    features_union['hour'] = intervals.apply(lambda x: x.mid.hour).values
    # source https://ianlondon.github.io/posts/encoding-cyclical-features-24-hour-time/
    features_union['sin_hour'] = np.sin(2 * np.pi * features_union.hour / 24)
    features_union['cos_hour'] = np.cos(2 * np.pi * features_union.hour / 24)
    features_union['day_period'] = features_union.hour.apply(determine_day_period)
    features_union = pd.get_dummies(features_union, columns=['day_period'], drop_first=True)

    return features_union


def main(path_to_sensors: List[Path], output_path):
    logger.info(f"merge all features for country'")

    X = get_x(path_to_sensors)
    X = X.reset_index()

    _intervalindex_to_columns(X)
    X.to_csv(output_path, index=False)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input', help='path to the sensor files', nargs='+')
    parser.add_argument('-o', '--output', help='output path')
    parser.add_argument('-l', '--log', help='path to logging file', default='final_data.log')
    args = parser.parse_args()

    logger = get_logger(os.path.basename(__file__), args.log)

    main([Path(p) for p in args.input], args.output)
    logger.info(f"Done!")

