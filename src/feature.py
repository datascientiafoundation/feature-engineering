import glob
import logging
import os
import time
import scipy
import numpy as np
import pandas as pd
from pathlib import Path
from src.utils.utils import _intervalindex_to_columns, get_logger, radius_of_gyration, get_total_distance_covered, \
    centermost_point

def compute_windows_intervals(contribution: pd.DataFrame, window_size_mins: int) -> pd.IntervalIndex:
    timestamp_col = 'timestamp'

    start = contribution[timestamp_col].min().floor(f'{window_size_mins}min')
    end = contribution[timestamp_col].max().ceil(f'{window_size_mins}min')

    bins = pd.date_range(
        start=start,
        end=end + pd.Timedelta(minutes=window_size_mins),
        freq=f'{window_size_mins}min'
    )

    intervals = pd.IntervalIndex.from_breaks(bins, closed='left')
    return intervals


# =======================================================================================
# ================================= CONNECTIVITY ========================================
# =======================================================================================

# def _compute_entropy(x):
#     return scipy.stats.entropy(x.value_counts(normalize=True, sort=False), base=10)
def _compute_entropy(x):
    counts = x.value_counts(normalize=True, sort=False)
    counts = counts.astype(float)
    return scipy.stats.entropy(counts, base=10)


def bluetoothdevices(groups, prefix=''):
    addresses = groups['address'].nunique().rename('addr_nuinque')
    # paper Smartphone bluetooth base social sensing
    entropy = groups['address'].apply(_compute_entropy).rename('entropy_basic')
    rssi = groups['rssi'].agg(['mean', 'min', 'max', 'std', 'var'])
    out = pd.concat([addresses, rssi, entropy], axis=1, verify_integrity=True)
    out = out.add_prefix(prefix)
    return out


def cellularnetwork(groups):
    n_devices = groups.cellid.agg(lambda x: len(np.unique(x))).rename('num_of_devices')
    entropy = groups.cellid.apply(_compute_entropy).rename('entropy_basic')
    phone_strength = groups.dbm.agg([np.mean, np.min, np.max, np.std])
    out = pd.concat([phone_strength, entropy, n_devices], axis=1, verify_integrity=True) \
        .add_prefix('cellular_lte_')
    return out


def wifi(groups):
    ft = groups.agg(wifi_is_connected=('isconnected', max))
    ft['wifi_is_connected'].fillna(False, inplace=True)

    ft['wifi_is_connected'] = ft['wifi_is_connected'].astype(float)

    return ft


def wifinetworks(groups):
    # wifi_num_of_devices,
    return groups.agg(
        num_of_devices=('address', lambda x: len(np.unique(x))),
        mean_rssi=('rssi', np.mean),
        min_rssi=('rssi', np.min),
        max_rssi=('rssi', np.max),
        std_rssi=('rssi', np.std)
    ).add_prefix('wifi_')


# =======================================================================================
# ================================= INERTIAL ========================================
# =======================================================================================


def _count_steps(x):
    y = x.sort_values('timestamp', ascending=True)
    y['change'] = y.value.diff()
    # set the value to zero if the counter is decreasing. Probably a reboot occurred
    y.loc[y['change'] < 0, 'value'] = 0
    # recompute difference between detections
    y['change'] = y.value.diff()
    # cancel negative variations between counter detections
    y['change'] = y['change'].clip(lower=0)
    sum_of_diff = y['change'].sum()
    return sum_of_diff


def stepcounter(groups):
    """https://developer.android.com/guide/topics/sensors/sensors_motion#sensors-motion-stepcounter"""
    return groups.apply(_count_steps).rename(
        'steps_counter').to_frame()  # added .to_frame() to convert it from series to dataframe


def stepdetector(groups):
    """https://developer.android.com/guide/topics/sensors/sensors_motion#sensors-motion-stepdetector"""
    return groups.size().rename(
        'steps_detected_count').to_frame()  # added .to_frame() to convert it from series to dataframe


# =======================================================================================
# ================================= POSITION ========================================
# =======================================================================================


def location_feature(groups):
    def _get_centermost_point(x):
        cluster = x[['latitude', 'longitude']].to_numpy()
        if len(cluster) > 0:
            point = centermost_point(cluster)
        else:
            # there shouldn't be empty groups, so this branch is not reachable
            # keep it for safety reasons
            raise ValueError(f'No gps coords u={x.userid} interval=[{x.interval}]')
        return pd.Series(point, index=['latitude', 'longitude'])

    df_centermost = groups.apply(_get_centermost_point)

    features = groups.agg({'longitude': [np.mean, np.min, np.max],
                           'latitude': [np.mean, np.min, np.max],
                           'altitude': [np.mean, np.min, np.max],
                           'speed': [np.mean, np.min, np.max, np.std]})
    features.columns = features.columns.map('_'.join)

    rog = groups.apply(radius_of_gyration).rename('radius_of_gyration')
    dist = groups.apply(get_total_distance_covered).rename('distance_sum')

    return df_centermost.join([features, rog, dist], validate='one_to_one').add_prefix('location_')


# =======================================================================================
# ================================= SOFTWARE ========================================
# =======================================================================================


def touch(groups):
    return groups.size().rename('touch_count').to_frame()


def notification(groups):
    return groups.status.value_counts().unstack()


# error_keys = set() #added
def application(groups):
    def _get_app_category(apps, category_db) -> pd.Series:
        categories = set()
        apps = apps.unique()
        for a in apps[apps != None]:
            try:  # added
                categories.add(category_db.loc[a, 'category'])  # change: genre -> category
            except KeyError as e:  # added
                # error_keys.add(a) #added
                # logger.warning(e)
                categories.add('app_not-found')  # added

        d = {k: 1 for k in categories}
        d['category_nunique'] = len(categories)
        s = pd.Series(data=d,
                      index=['category_nunique'] + list(category_db['category'].unique()))
        return s

    category_db = pd.read_csv(Path('src', 'utils', 'appcategories.csv'))
    category_db.drop_duplicates(inplace=True)
    category_db.set_index('app_id', verify_integrity=True, inplace=True)
    app_stats = groups['applicationname'].nunique().rename('nunique')
    categories_stat = groups['applicationname'].apply(_get_app_category,
                                                      category_db).unstack()
    entropy = groups['applicationname'].agg(_compute_entropy).rename('entropy_basic')
    out = pd.concat([categories_stat, app_stats, entropy], axis=1, verify_integrity=True).add_prefix('app_')
    out.columns = [c.replace(' ', '_').lower() for c in out.columns]
    out = out.fillna(0)
    return out


def batterymonitoringlog(groups):
    """https://developer.android.com/training/monitoring-device-state/battery-monitoring#CurrentLevel"""

    ft = groups \
        .apply(lambda x: x.sort_values('timestamp', ascending=True)) \
        .groupby(level=[0, 1, 2])[['timestamp', 'level', 'scale']] \
        .agg({'timestamp': ['first', 'last'], 'level': ['first', 'last'], 'scale': ['mean']})

    ft.columns = ft.columns.map('_'.join)
    ft['level_last'] = ft['level_last'] * 100 / ft['scale_mean']
    ft['level_first'] = ft['level_first'] * 100 / ft['scale_mean']
    ft = ft.assign(delta=lambda x: (x['level_last'] - x['level_first']))
    ft = ft.add_prefix('battery_')
    return ft


# =======================================================================================
# ================================= GENERICS ========================================
# =======================================================================================


def value_feature(groups, column_name, prefix=''):
    return groups[column_name].agg([np.mean, np.std, np.min, np.max]).add_prefix(prefix)


def xyz_feature(groups, prefix=''):
    def _compute_stats(x):
        return x \
            .assign(magnitude=lambda row: np.linalg.norm(row[['x', 'y', 'z']], axis=1))[['x', 'y', 'z', 'magnitude']] \
            .agg(['min', 'max', 'mean', 'std'])

    tmp = groups.apply(_compute_stats).unstack()
    tmp.columns = tmp.columns.map('_'.join)
    return tmp.add_prefix(prefix)


def xyz_unc_feature(groups, prefix=''):
    def _compute_stats(x):
        # Compute magnitude first
        x = x.assign(magnitude=lambda row: np.linalg.norm(row[['x', 'y', 'z']], axis=1))

        # Keep only relevant columns for aggregation
        cols = ['x', 'y', 'z', 'xunc', 'yunc', 'zunc', 'magnitude']
        return x[cols].agg(['min', 'max', 'mean', 'std'])

    tmp = groups.apply(_compute_stats).unstack()
    tmp.columns = tmp.columns.map('_'.join)  # flatten multiindex
    return tmp.add_prefix(prefix)


def xyz_accuracy_scalar_feature(groups, prefix=''):
    def _compute_stats(x):
        # Calculate the magnitude for x, y, z
        x = x.assign(magnitude=lambda row: np.linalg.norm(row[['x', 'y', 'z']], axis=1))

        # Aggregate the statistics for x, y, z, magnitude, accuracy, and scalar
        stats = x[['x', 'y', 'z', 'magnitude', 'accuracy', 'scalar']].agg(['min', 'max', 'mean', 'std'])

        return stats

    # Apply the feature computation function and unstack the result
    tmp = groups.apply(_compute_stats).unstack()

    # Flatten the multi-level columns and join them
    tmp.columns = tmp.columns.map('_'.join)

    # Add the prefix to the columns
    return tmp.add_prefix(prefix)


def on_change_feature(groups, sensor_df, sensor_name: str, column_name: str, states: list, prefix='',
                      unknown_state=None) -> pd.DataFrame:
    """compute features for on-change sensors, e.g., screen status.
    The method counts the seconds each state is active"""

    # get window size from interval index
    # TODO rimettere quello che c'era prima
    window_size = 30

    timestamps = None
    if len(states) > 2:
        timestamps = pd.DatetimeIndex(data=sensor_df.timestamp)
        timestamps = timestamps.sort_values()
        assert timestamps.is_monotonic_increasing

    duration_per_group = []
    for (userid, experimentid, interval), gr in groups:
        # compute how many seconds there are from on state change to another
        gr.sort_values(by='timestamp', ascending=True, inplace=True)
        gr['duration'] = gr.timestamp.diff(periods=1).shift(-1).dt.total_seconds()

        # add elapsed time from the last sensor reading to the end of the window
        assert np.isnan(gr.loc[gr.index[-1], 'duration'])
        gr.loc[gr.index[-1], 'duration'] = (gr.iloc[-1].interval.right - gr.iloc[-1].timestamp).total_seconds()

        total_duration = gr.groupby([column_name]).duration.sum()
        total_duration['interval'] = interval
        total_duration['userid'] = userid
        total_duration['experimentid'] = experimentid

        # states that are not observed in a window to zero
        for state in states:
            if state not in total_duration.index:
                total_duration[state] = 0

        # ==================
        # count number of episodes (ON and then OFF)

        if sensor_name == 'screen':
            # it can happen that there are sequence of on and off, they are not always interspersed
            # groupby when the status changes from row to row
            grouped_sequences = gr \
                .groupby([(gr.status != gr.status.shift()).cumsum(), gr.status])['duration'] \
                .sum() \
                .reset_index(level=0, drop=True) \
                .reset_index()  # reset sequence idx and reset status idx
            # find episodes
            grouped_sequences['episode'] = ((grouped_sequences.status == 'SCREEN_ON') & (
                    grouped_sequences.status.shift(-1) == 'SCREEN_OFF'))

            stats = grouped_sequences[grouped_sequences['episode']] \
                .groupby('status')['duration'] \
                .agg(['size', 'mean', 'min', 'max', 'std'])

            assert len(stats) <= 1
            stats = stats.reset_index()
            total_duration['episodes_count'] = stats.iloc[0]['size'] if len(stats) > 0 else 0
            total_duration['mean_seconds_per_episode'] = stats.iloc[0]['mean'] if len(stats) > 0 else 0
            total_duration['min_seconds_per_episode'] = stats.iloc[0]['min'] if len(stats) > 0 else 0
            total_duration['max_seconds_per_episode'] = stats.iloc[0]['max'] if len(stats) > 0 else 0
            total_duration['std_seconds_per_episode'] = stats.iloc[0]['std'] if len(stats) > 0 else 0
            if pd.isna(total_duration['std_seconds_per_episode']):  # is NaN if only one episode
                total_duration['std_seconds_per_episode'] = 0

        # ==================
        # add time from the beginning of the window to the first sensor reading
        if len(states) == 2:
            # given that there are only 2 possible states,
            # get the opposite state with respect to the first sensor reading.
            # This applies to sensors like screen status
            # Warning: there are no guarantees that previous status was the opposite one.
            # Sometimes there is a sequence of reading reporitng the same state.
            previous_last_state = [s for s in states if s != gr.iloc[0][column_name]][0]
        else:
            # this branch is used by activitiespertime
            # if multiple possible states, take the last sensor readings before
            # the start of the current time window. Please note that I cannot take the last value in the previous group
            # because there might be a gap between the windows. It depends on the window size around the contribution
            # questions
            previous_last_state = unknown_state
            first_ts_index = timestamps.get_loc(gr.iloc[0].timestamp)
            if first_ts_index - 1 >= 0:
                nearest_previous_sensor_reading_timestamp = timestamps[first_ts_index - 1]
                nearest_previous_sensor_reading = sensor_df.loc[
                    sensor_df.timestamp == nearest_previous_sensor_reading_timestamp]
                assert len(nearest_previous_sensor_reading) == 1
                nearest_previous_sensor_reading = nearest_previous_sensor_reading.iloc[0]
                if sensor_name in ['userpresence', 'screen']:
                    # 30 minutes is the frequency of the questions, if the previous sensor reading is too far away,
                    # discard it. This sensors shouldn't have a long gap between to sensor readings
                    threshold = pd.Timedelta(minutes=window_size)
                else:
                    threshold = pd.Timedelta(weeks=1000)
                if (gr.iloc[0].timestamp - nearest_previous_sensor_reading.timestamp) <= threshold:
                    previous_last_state = nearest_previous_sensor_reading[column_name]

            if previous_last_state is None and first_ts_index - 1 >= 0:
                raise ValueError('There is an error, this line shouldn\'t be reached')

        if previous_last_state is not None:
            total_duration[previous_last_state] += (gr.iloc[0].timestamp - gr.iloc[0].interval.left).total_seconds()

        # ==================

        assert total_duration.notna().all()
        duration_per_group.append(total_duration)

    duration_per_group = pd.concat(duration_per_group, axis=1).T
    duration_per_group = duration_per_group.set_index(['userid', 'experimentid', 'interval'], verify_integrity=True)
    # states that are not observed in a window to zero
    duration_per_group[states] = duration_per_group[states].fillna(0)

    # assert that total duration is not longer than the window size
    assert (duration_per_group[states].sum(axis=1) <= (window_size * 60) + 1e-4).all()

    duration_per_group.columns.name = None
    return duration_per_group.add_prefix(prefix)


def main(input_path: Path, output_path: Path, window_size_mins: int):
    sensor_name = input_path.stem
    sensor_name = sensor_name.replace('event', '')
    logger.info(f"Start feature generation sensor={sensor_name}")
    start = time.time()
    logger.info('Loading dataset...')
    sensor = pd.read_parquet(input_path)
    logger.info(f'Full dataset length: {len(sensor)}')

    sensor['timestamp'] = pd.to_datetime(sensor['timestamp'], format='%m%d%H%M%S%f')
    sensor['timestamp'] = sensor['timestamp'].dt.tz_localize(None)  # Removes the timezone
    sensor['timestamp'] = sensor['timestamp'].astype('datetime64[ns]')

    logger.info(f'Timestamp format changed ')
    if 'day' in sensor.columns:
        sensor.pop('day')
    if sensor.index.has_duplicates:
        logger.warning('Reset index of the sensor, there are duplicates')
        sensor = sensor.reset_index(drop=True)
    if sensor_name == 'batterycharge':
        sensor.source.replace(np.nan, 'no_charging', inplace=True)

    user_ids = sensor.userid.unique().tolist()
    features = []
    for user in user_ids:

        logger.info(f'user={user}')
        sensor_user = sensor[sensor.userid == user].copy()
        intervals = compute_windows_intervals(sensor_user, window_size_mins)
        sensor_user['interval'] = pd.cut(sensor_user.timestamp, intervals, duplicates='raise')

        on_change_sensors = {
            'screen': dict(prefix='screen_'),
            'activities': dict(prefix='activity_', column='label', unknown_state='Unknown'),
            'batterycharge': dict(prefix='battery_', column='source', unknown_state='no_charging'),
            'userpresence': dict(prefix='user_presence_'),
            'airplanemode': dict(prefix='airplanemode_'),
            'headsetplug': dict(prefix='headset_'),
            'ringmode': dict(prefix='ringmode_'),
            'music': dict(prefix='music_'),
            'doze': dict(prefix='doze_'),
        }

        value_sensors = {'proximity': 'proximity_',
                         'light': 'light_',
                         'pressure': 'pressure_',
                         'ambienttemperature': 'ambienttemperature_',
                         'relativehumidity': 'relative_humidity_',}

        groupbycolumns = ['userid', 'experimentid', 'interval']

        groups = sensor_user.groupby(groupbycolumns, sort=True, group_keys=True)

        if sensor_name in value_sensors.keys():
            ft = value_feature(groups, 'value', value_sensors[sensor_name])
        elif sensor_name == 'wifi':
            ft = wifi(groups)
        elif sensor_name == 'wifinetworks':
            ft = wifinetworks(groups)
        elif sensor_name in ['location', 'location']:
            ft = location_feature(groups)
        elif sensor_name == 'cellularnetwork':
            groups = sensor_user.loc[sensor_user['type'] == 'lte'].groupby(groupbycolumns, sort=True, group_keys=True)
            ft = cellularnetwork(groups)
        elif sensor_name == 'stepdetector':
            ft = stepdetector(groups)
        elif sensor_name == 'stepcounter':
            ft = stepcounter(groups)
        elif sensor_name == 'touch':
            ft = touch(groups)
        elif sensor_name == 'notification':
            ft = notification(groups)
        elif sensor_name == 'applications':
            ft = application(groups)
        elif sensor_name in ['batterymonitoringlog', 'batterylevel']:
            ft = batterymonitoringlog(groups)
        elif sensor_name in ['bluetoothnormal', 'bluetoothlowenergy',
                             'bluetooth']:  # added bluetooth
            ft = bluetoothdevices(groups, prefix=sensor_name + '_')
        elif sensor_name in ['gyroscope', 'magneticfield', 'accelerometer', 'gravity', 'orientation', 'linearacceleration']:
            ft = xyz_feature(groups, prefix=sensor_name + '_')
        elif sensor_name in ['accelerometeruncalibrated', 'magneticfielduncalibrated', 'gyroscopeuncalibrated']:
            ft = xyz_unc_feature(groups, prefix=sensor_name + '_')
        elif sensor_name in ['rotationvector', 'geomagneticrotationvector']:
            ft = xyz_accuracy_scalar_feature(groups, prefix=sensor_name + '_')

        elif sensor_name in on_change_sensors.keys():
            column_name = on_change_sensors[sensor_name].get('column', 'status')

            possible_states = sensor[column_name].unique().tolist()
            possible_states = [str(s) for s in possible_states]

            if len(possible_states) < 2:
                raise ValueError(f'on-change sensor "{sensor_name}" has only less than 2 states ')

            sensor_user[column_name] = sensor_user[column_name].astype('string')
            groups = sensor_user.groupby(groupbycolumns, sort=True)

            if groups.size().max() == 0:
                logger.warning(f'Skip user={user}": all valid windows are empty')
                continue

            ft = on_change_feature(groups,
                                   sensor_user,
                                   sensor_name=sensor_name,
                                   column_name=column_name,
                                   states=possible_states,
                                   prefix=on_change_sensors[sensor_name]['prefix'],
                                   unknown_state=on_change_sensors[sensor_name].get('unknown_state', None)
                                   )
        else:
            raise ValueError(f"No features defined for the sensor '{sensor_name}'!")

        features.append(ft)

    if len(features) == 0:
        # raise ValueError('None of the users has features, investigate the reason')
        logger.info('None of the users has features')
        logger.info('feature engineering skipped')
        logger.info(f'Completed in {round(time.time() - start)} [s]')
        return

    features = pd.concat(features, axis=0)
    features = features.reset_index(names=['userid', 'experimentid', 'interval'])
    _intervalindex_to_columns(features)
    if os.path.splitext(output_path)[-1] == '.csv':
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        features.to_csv(output_path, index=False)
    elif os.path.splitext(output_path)[-1] == '.parquet':
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        features.to_parquet(output_path, engine='pyarrow')
    else:
        raise ValueError(f'The output format is not known ({output_path})')
    logger.info(f'Completed in {round(time.time() - start)} [s]')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input')
    parser.add_argument('-o', '--output')
    parser.add_argument('-l', '--logs',
                        help='path to logging file')
    parser.add_argument('-t', '--window-size', type=int)
    args = parser.parse_args()

    logger = get_logger(os.path.basename(__file__), args.logs)

    main(Path(args.input), Path(args.output), args.window_size)
