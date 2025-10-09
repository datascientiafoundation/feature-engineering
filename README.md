


# Feature Engineering

This repository contains the code to generate features from the raw data available on the [LivePeople data catalog](https://datascientiafoundation.github.io/LivePeople) powered by [Datascientia](https://datascientia.eu/). The following code has been tested on [DivesityOne dataset](https://datascientia.eu/projects/diversityone/).

All features in this repository are extracted over **fixed-length time intervals**.

Each user's data is divided into consecutive, non-overlapping time windows (e.g., 30-minute segments), and features are computed **independently for each interval**. This time-based aggregation applies to all supported sensor types (e.g., accelerometer, screen, wifi, etc.).

Typical usage of the features is for training machine learning models and for people’s everyday life behavior analysis with mobile data, e.g., behavioral changes over time.

Details about the datasets can be found on [LivePeople data catalog](https://datascientiafoundation.github.io/LivePeople). 

A sample test dataset is provided in the [`test/`](test) directory for quick experimentation and development.


## Requirements

- Python 3.9
- Snakemake (for workflow automation)

## Installation

Clone the repository

```bash
git clone git@github.com:datascientiafoundation/feature-engineering.git
```

Create a new environment with [Conda](https://docs.conda.io/en/latest/)

```bash
conda env create -f environment.yml
conda activate feature_env
```

To install Snakemake, use the following command:

```bash
pip install snakemake
```

## Repository structure

```
.
├── config/
│   ├── config.yaml              # Contains a list of countries and sensors 
├── data/
│   ├── CREP/                    # Datasets following the CREP structure (Hierarchical)
│   ├── interim/                 # Intermediate files, single sensor features
│   ├── raw/                     # Raw datasets
│   └── processed/               # Processed datasets, aggregated features
├── logs/
├── src/
│   ├── utils/
│   │   ├── appcategories.csv    # Contains mapping related to application categories
│   │   └── utils.py             # Utility functions for the project
│   ├── config.py                # Handles loading or managing configuration settings
│   ├── contribution.py          # Logic related to computing or managing user contributions
│   ├── feature.py               # Script for performing feature engineering on a single dataset
│   ├── join_features.py         # Script for merging/joining features from different sensors
│   └── load.py                  # Script for loading datasets
├── test/			 # Test dataset (input, output)
├── CITATION.cff
├── environment.yml              # Conda environment configuration file
├── LICENCE                      # Contains the license information for the project (e.g., MIT License)
├── README.md
└── Snakefile                    # Defines the workflow for processing datasets

```

## Data preparation

Download the dataset (the datasets can be requested on the [Datascientia platform](https://ds.datascientia.eu/marketplace/welcome)) and save it in the appropriate folder:
   
   - If the dataset follows the **flattened structure**, save it in the `data/raw` folder.
   
   - If the dataset follows the **Hierarchical structure** (as retrieved from the catalog), save it in the `data/CREP` folder. Datasets in this structure need to be flattened first by running the following script:

    ```bash
     python -m src.load -i data/CREP -o data/raw -l logs/load.log
    ```


## Workflow Description

The Snakemake workflow orchestrates the end-to-end processing of datasets located in the [data/raw](data/raw) directory.
The pipeline proceeds through the following stages:

1.  **Process Time Diary**  
    The workflow begins by processing the time diary data, which defines valid activity intervals for each user.
    
2.  **Process Single Sensors**  
    Using the time intervals extracted from the processed timediary, each sensor dataset is processed individually to extract features. The resulting features are stored in the [data/interim](data/interim) directory.
    
3.  **Join Features**  
    Finally, all single-sensor features are joined based on their timestamps, resulting in a unified, time-aligned dataset saved in the [data/processed](data/processed) directory.
    
To run the entire workflow, execute the following command:

```bash
snakemake all --cores 1
```

### Configuration

**`config.yaml`** includes the following settings:

-   **Available Datasets**:  
    A strict list of dataset names. Only the sensors explicitly listed here will be processed—any sensor not listed will be ignored, even if present.
    
-   **Time Diary Inclusion**:  
    A boolean flag that controls whether time diary data should be included in feature generation.
    
- **Sensor Frequency (`freq`)**: Specifies the duration of each time window in minutes.
	-   _When using time diary_:  
    For instance, if `freq` is set to 30 minutes and time diary entries occur every 30 minutes, each time window spans from 15 minutes before to 15 minutes after a time diary timestamp. Sensor events within these windows are aggregated to generate features.
 
	-	_When not using time diary_:  
    The entire sensor data timeline is divided into consecutive, non-overlapping intervals of fixed length. For example, if `freq` is set to 30 minutes, intervals like [10:00–10:30), [10:30–11:00), and so on are created. Sensor events are assigned to these intervals based on their timestamps, and features are aggregated accordingly.

## Process single dataset

You can process a single dataset using the [src/feature.py](src/feature) script directly:

```bash
python -m src.feature -i data/raw/<SENSOR>.parquet \
                      -t data/interim/timediary.csv \
                      -o data/interim/<SENSOR>.csv \
                      -l logs/<SENSOR>.log \
                      -f <FREQ> \
                      -ti True
```
Example: 

```bash
python -m src.feature -i data/raw/accelerometer.parquet \
                      -t data/interim/timediary.csv \
                      -o data/interim/accelerometer.csv \
                      -l logs/accelerometer.log  \
                      -f 30 \
                      -ti True
```

 ## Workflow without timediary

if you want to process datasets without timediary intervals, you can change the **timediary** 
parameter in [config/config.yaml](config/config.yaml) to **False**. Then the run the workflow as: 

```bash
snakemake all --cores 1
```

#### To process single dataset without timediary:

```bash
python -m src.feature -i data/raw/<SENSOR>.parquet \
                      -t data/interim/timediary.csv \
                      -o data/interim/<SENSOR>.csv \
                      -l logs/<SENSOR>.log \
                      -f <FREQ> \
                      -ti False
```


## Supported Datasets and Extracted Features

<!-- TOC -->
* [Cyclical Feature Encoding](#cyclical-feature-encoding)
* [Environment](#environment)
  * [`ambienttemperature`](#ambienttemperature)
  * [`light`](#light)
  * [`pressure`](#pressure)
  * [`relativehumidity`](#relativehumidity)
* [Application usage](#application-usage)
  * [`airplanemode`](#airplanemode)
  * [`applications`](#applications)
  * [`headsetplug`](#headsetplug)
  * [`music`](#music)
  * [`notification`](#notification)
* [Device usage](#device-usage)
  * [`batterycharge`](#batterycharge)
  * [`batterylevel`](#batterylevel)
  * [`doze`](#doze)
  * [`ringmode`](#ringmode)
  * [`screen`](#screen)
* [Position](#position)
  * [`location`](#location)
  * [`orientation`](#orientation)
  * [`proximity`](#proximity)
  * [`rotationvector`](#rotationvector)
  * [`magneticfield`](#magneticfield)
  * [`magneticfielduncalibrated`](#magneticfielduncalibrated)
  * [`geomagneticrotationvector`](#geomagneticrotationvector)
* [Motion](#motion)
  * [`accelerometer`](#accelerometer-)
  * [`accelerometeruncalibrated`](#accelerometeruncalibrated)
  * [`linearacceleration`](#linearacceleration)
  * [`activities`](#activities)
  * [`gravity`](#gravity)
  * [`gyroscope`](#gyroscope)
  * [`gyroscopeuncalibrated`](#gyroscopeuncalibrated)
  * [`stepcounter`](#stepcounter)
  * [`stepdetector`](#stepdetector)
  * [`touch`](#touch)
* [Connectivity](#connectivity)
  * [`bluetooth`](#bluetooth)
  * [`cellularnetwork`](#cellularnetwork)
  * [`wifi`](#wifi)
  * [`wifinetworks`](#wifinetworks)
<!-- TOC -->

### Cyclical Feature Encoding


| Feature name           | Type           | Description                                             |
|------------------------|----------------|---------------------------------------------------------|
| `hour`                 | integer [0,23] | hour of the window start                                |
| `sin_hour`, `cos_hour` | float [0,1]    | sine and cosine of the hour                             |
| `day_period_morning`   | boolean        | hour of the window star is between 6:00 am and 9:59 am  |
| `day_period_noon`      | boolean        | hour of the window star is between 10:00 am and 1:59 pm |
| `day_period_evening`   | boolean        | hour of the window star is between 2:00 pm and 5:59 pm  |
| `day_period_aftenoon`  | boolean        | hour of the window star is between 6:00 pm and 9:59 pm  |
| `day_period_nigth`     | boolean        | hour of the window star is between 10:00 pm and 5:59 am |

Cyclical features, such as the hour of the day, are also added to the dataset in order to capture the circular nature of time.
This encoding technique helps models understand that certain times are close to others, such as 23:00 being close to 00:00.
By using sine and cosine transformations, these features are represented in a way that preserves their cyclical nature,
which improves the performance of models that involve time-based patterns.

Source: [Encoding Cyclical Features](https://ianlondon.github.io/posts/encoding-cyclical-features-24-hour-time/)


### Environment

####   `ambienttemperature`
- `min`, `std`, `min`, `max`

####   `light`
- `min`, `std`, `min`, `max`

####   `pressure`
- `min`, `std`, `min`, `max`

####  `relativehumidity`
- `min`, `std`, `min`, `max`

### Application usage

####   `airplanemode`
 - `airplanemode_True`, `airplanemode_False`

####   `applications`
- `app_category_nunique`
- `[application groups]`
- `app_nunique`, `app_entropy_basic` 

####   `headsetplug`
- `headset_False`, `headset_True`

####   `music`
- `music_False`, `music_True`

####   `notification`
- `notification_posted`, `notification_removed`

### Device usage

####   `batterycharge`
- `battery_charging_ac`, `battery_no_charging`, `battery_charging_unknown`
    
####   `batterylevel`

| Feature name                                        | Type | Description |
|-----------------------------------------------------|------|-------------|
| `battery_level_first`, `battery_level_last`         |      |             |
| `battery_scale_mean`                                |      |             |
| `battery_delta`                                     |      |             |

    
####   `doze`
- `doze_True`, `doze_False`

####   `ringmode`
- `ringmode_mode_silent`, `ringmode_mode_normal`, `ringmode_mode_vibrate`

####   `screen`

- `screen_SCREEN_ON`, `screen_SCREEN_OFF`, `screen_episodes_count`, 
- `screen_mean_seconds_per_episode`, `screen_min_seconds_per_episode`, `screen_max_seconds_per_episode`, `screen_std_seconds_per_episode`

### Position

####   `location`
- `latitude`, `longitude`, 
- `longitude_mean`, `longitude_min`, `longitude_max`, 
- `latitude_mean`, `latitude_min`, `latitude_max`, 
- `altitude_mean`, `altitude_min`, `altitude_max`, 
- `speed_mean`, `speed_min`, `speed_max`, `speed_std`, 
- `radius_of_gyration`, `distance_sum`


####   `orientation`
- `x_min`, `x_max`, `x_mean`, `x_std`
- `y_min`, `y_max`, `y_mean`, `y_std`
- `z_min`, `z_max`, `z_mean`, `z_std`
- `magnitude_min`, `magnitude_max`, `magnitude_mean`, `magnitude_std`

####   `proximity`
- `min`, `std`, `min`, `max`

####   `rotationvector`
- `x_min`, `x_max`, `x_mean`, `x_std`
- `y_min`, `y_max`, `y_mean`, `y_std`
- `z_min`, `z_max`, `z_mean`, `z_std`
- `magnitude_min`, `magnitude_max`, `magnitude_mean`, `magnitude_std`
- `accuracy_min`, `accuracy_max`, `accuracy_mean`, `accuracy_std`
- `scalar_min`, `scalar_max`, `scalar_mean`, `scalar_std`

####   `magneticfield`
- `x_min`, `x_max`, `x_mean`, `x_std`
- `y_min`, `y_max`, `y_mean`, `y_std`
- `z_min`, `z_max`, `z_mean`, `z_std`
- `magnitude_min`, `magnitude_max`, `magnitude_mean`, `magnitude_std`
    
####   `magneticfielduncalibrated`
- `x_min`, `x_max`, `x_mean`, `x_std`
- `y_min`, `y_max`, `y_mean`, `y_std`
- `z_min`, `z_max`, `z_mean`, `z_std`
- `xunc_min`, `xunc_max`, `xunc_mean`, `xunc_std`
- `yunc_min`, `yunc_max`, `yunc_mean`, `yunc_std`
- `zunc_min`, `zunc_max`, `zunc_mean`, `zunc_std`
- `magnitude_min`, `magnitude_max`, `magnitude_mean`, `magnitude_std`

####   `geomagneticrotationvector`
- `x_min`, `x_max`, `x_mean`, `x_std`
- `y_min`, `y_max`, `y_mean`, `y_std`
- `z_min`, `z_max`, `z_mean`, `z_std`
- `magnitude_min`, `magnitude_max`, `magnitude_mean`, `magnitude_std`
- `accuracy_min`, `accuracy_max`, `accuracy_mean`, `accuracy_std`
- `scalar_min`, `scalar_max`, `scalar_mean`, `scalar_std`

### Motion

#### `accelerometer` 
- `x_min`, `x_max`, `x_mean`, `x_std`
- `y_min`, `y_max`, `y_mean`, `y_std`
- `z_min`, `z_max`, `z_mean`, `z_std`
- `magnitude_min`, `magnitude_max`, `magnitude_mean`, `magnitude_std`
 
####   `accelerometeruncalibrated`
- `x_min`, `x_max`, `x_mean`, `x_std`
- `y_min`, `y_max`, `y_mean`, `y_std`
- `z_min`, `z_max`, `z_mean`, `z_std`
- `xunc_min`, `xunc_max`, `xunc_mean`, `xunc_std`
- `yunc_min`, `yunc_max`, `yunc_mean`, `yunc_std`
- `zunc_min`, `zunc_max`, `zunc_mean`, `zunc_std`
- `magnitude_min`, `magnitude_max`, `magnitude_mean`, `magnitude_std`

####  `linearacceleration`
- `x_min`, `x_max`, `x_mean`, `x_std`
- `y_min`, `y_max`, `y_mean`, `y_std`
- `z_min`, `z_max`, `z_mean`, `z_std`
- `magnitude_min`, `magnitude_max`, `magnitude_mean`, `magnitude_std`

####  `activities`
- `activity_Running` ,`activity_Unknown`, `activity_Tilting`, `activity_OnBicycle`, `activity_InVehicle`, `activity_Still`, `activity_Walking`, `activity_OnFoot`,
    
####   `gravity`
- `x_min`, `x_max`, `x_mean`, `x_std`
- `y_min`, `y_max`, `y_mean`, `y_std`
- `z_min`, `z_max`, `z_mean`, `z_std`
- `magnitude_min`, `magnitude_max`, `magnitude_mean`, `magnitude_std`
    
####   `gyroscope`
- `x_min`, `x_max`, `x_mean`, `x_std`
- `y_min`, `y_max`, `y_mean`, `y_std`
- `z_min`, `z_max`, `z_mean`, `z_std`
- `magnitude_min`, `magnitude_max`, `magnitude_mean`, `magnitude_std`
    
####   `gyroscopeuncalibrated`
- `x_min`, `x_max`, `x_mean`, `x_std`
- `y_min`, `y_max`, `y_mean`, `y_std`
- `z_min`, `z_max`, `z_mean`, `z_std`
- `xunc_min`, `xunc_max`, `xunc_mean`, `xunc_std`
- `yunc_min`, `yunc_max`, `yunc_mean`, `yunc_std`
- `zunc_min`, `zunc_max`, `zunc_mean`, `zunc_std`
- `magnitude_min`, `magnitude_max`, `magnitude_mean`, `magnitude_std`

####   `stepcounter`
- `steps_counter` 
    
####   `stepdetector`
- `steps_detected_count`

####   `touch`
- `touch_count` 

### Connectivity

####   `bluetooth`
- `bluetooth_addr_nunique`, `bluetooth_mean`, `bluetooth_min`, `bluetooth_max`, `bluetooth_std`, `bluetooth_var`, `bluetooth_entropy_basic,`

####   `cellularnetwork`

| Feature name                         | Type  | Description                                          |
|--------------------------------------|-------|------------------------------------------------------|
| `cellular_lte_{mean, min, max, std}` | float | descriptive statistics of the signal strength values |
| `cellular_lte_entropy_basic`         | float | entropy of the cellular ids                          |
| `cellular_lte_num_of_devices`        | count | number of unique                                     |


####   `wifi`

| Feature name        | Type    | Description                                                                     |
|---------------------|---------|---------------------------------------------------------------------------------|
| `wifi_is_connected` | boolean | Whether the device connected to a WiFi network at least once in the time window |
    
####   `wifinetworks`

| Feature name                                                        | Type    | Description                                                                                           |
|---------------------------------------------------------------------|---------|-------------------------------------------------------------------------------------------------------|
| `wifi_num_of_devices`                                               | integer | Number of unique scanned networks                                                                     |
| `wifi_mean_rssi`, `wifi_min_rssi`, `wifi_max_rssi`, `wifi_std_rssi` | float   | Mean, min, max and variance of the Received Signal Strength Indicator (RSSI) of the detected networks |                                  |
 
