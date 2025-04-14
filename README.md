


# Feature Engineering

This repository contains the code to generate features from the raw data available on the [LivePeople data catalog](https://datascientiafoundation.github.io/LivePeople) powered by [Datascientia](https://datascientia.eu/). The following code has been tested on [DivesityOne dataset](https://datascientia.eu/projects/diversityone/).

All features in this repository are extracted over **fixed-length time intervals**.

Each user's data is divided into consecutive, non-overlapping time windows (e.g., 30-minute segments), and features are computed **independently for each interval**. This time-based aggregation applies to all supported sensor types (e.g., accelerometer, screen, wifi, etc.).

Typical usage of the features is for training machine learning models and for people’s everyday life behavior analysis with mobile data, e.g., behavioral changes over time.

Details about the datasets can be found on [LivePeople data catalog](https://datascientiafoundation.github.io/LivePeople). 


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
├── test/						 # Test dataset (input, output)
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

The Snakemake workflow orchestrates the end-to-end processing of datasets located in the [data/raw](data/raw) directory. The pipeline proceeds through the following stages:

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
    
- **Sensor Frequency (`freq`)**:  
Specifies the duration of each time window in minutes.
	-   When using time diary:  
    For instance, if `freq` is set to 30 minutes and time diary entries occur every 30 minutes, each time window spans from 15 minutes before to 15 minutes after a time diary timestamp. Sensor events within these windows are aggregated to generate features.
 
	-	When not using time diary:  
    The entire sensor data timeline is divided into consecutive, non-overlapping intervals of fixed length. For example, if `freq` is set to 30 minutes, intervals like [10:00–10:30), [10:30–11:00), and so on are created. Sensor events are assigned to these intervals based on their timestamps, and features are aggregated accordingly.

## Process single dataset
You can process a single dataset using the [src/feature.py](src/feature) script directly:
```bash
python -m src.feature -i data/raw/<SENSOR>.parquet -t data/interim/timediary.csv -o data/interim/<SENSOR>.csv -l logs/<SENSOR>.log -f <FREQ> -ti True
```
Example: 
```bash
python -m src.feature -i data/raw/accelerometer.parquet -t data/interim/timediary.csv -o data/interim/accelerometer.csv -l logs/accelerometer.log -f 30 -ti True
```

 ## Workflow without timediary
if you want to process datasets without timediary invervals, you can change the **timediary** parameter in [config/config.yaml](config/config.yaml) to **False**. Then the run the workflow as: 
```bash
snakemake all --cores 1
```

#### To process single datset without timediary: 
```bash
python -m src.feature -i data/raw/<SENSOR>.parquet -t data/interim/timediary.csv -o data/interim/<SENSOR>.csv -l logs/<SENSOR>.log -f <FREQ> -ti False
```

### Cyclical Feature Encoding

Cyclical features, such as the hour of the day, are also added to the dataset in order to capture the circular nature of time. This encoding technique helps models understand that certain times are close to others, such as 23:00 being close to 00:00. By using sine and cosine transformations, these features are represented in a way that preserves their cyclical nature, which improves the performance of models that involve time-based patterns.

Source: [Encoding Cyclical Features](https://ianlondon.github.io/posts/encoding-cyclical-features-24-hour-time/)


## Supported Datasets and Extracted Features

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
    
####  `activities`
- `activity_Running` ,`activity_Unknown`, `activity_Tilting`, `activity_OnBicycle`, `activity_InVehicle`, `activity_Still`, `activity_Walking`, `activity_OnFoot`,
    
####   `airplanemode`
 - `airplanemode_True`, `airplanemode_False`
    
####   `ambienttemperature`
- `min`, `std`, `min`, `max`
    
####   `applications`
- `app_category_nunique`
- `[application groups]`
- `app_nunique`, `app_entropy_basic` 

####   `batterycharge`
- `battery_charging_ac`, `battery_no_charging`, `battery_charging_unknown`
    
####   `batterylevel`
- `battery_timestamp_first`, `battery_timestamp_last`, `battery_level_first`, `battery_level_last`, `battery_scale_mean`, `battery_delta` 
    
####   `bluetooth`
- `bluetooth_addr_nuinque`, `bluetooth_mean`, `bluetooth_min`, `bluetooth_max`, `bluetooth_std`, `bluetooth_var`, `bluetooth_entropy_basic,`
    
####   `cellularnetwork`
- `cellular_lte_mean`, `cellular_lte_min`, `cellular_lte_max`, `cellular_lte_std`,
- `cellular_lte_entropy_basic`, `cellular_lte_num_of_devices`
    
####   `doze`
- `doze_True`, `doze_False`
    
####   `geomagneticrotationvector`
- `x_min`, `x_max`, `x_mean`, `x_std`
- `y_min`, `y_max`, `y_mean`, `y_std`
- `z_min`, `z_max`, `z_mean`, `z_std`
- `magnitude_min`, `magnitude_max`, `magnitude_mean`, `magnitude_std`
- `accuracy_min`, `accuracy_max`, `accuracy_mean`, `accuracy_std`
- `scalar_min`, `scalar_max`, `scalar_mean`, `scalar_std`
    
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
    
####   `headsetplug`
- `headset_False`, `headset_True`
    
####   `light`
- `min`, `std`, `min`, `max`
    
####  `linearacceleration`
- `x_min`, `x_max`, `x_mean`, `x_std`
- `y_min`, `y_max`, `y_mean`, `y_std`
- `z_min`, `z_max`, `z_mean`, `z_std`
- `magnitude_min`, `magnitude_max`, `magnitude_mean`, `magnitude_std`
    
####   `location`
- `latitude`, `longitude`, 
- `longitude_mean`, `longitude_min`, `longitude_max`, 
- `latitude_mean`, `latitude_min`, `latitude_max`, 
- `altitude_mean`, `altitude_min`, `altitude_max`, 
- `speed_mean`, `speed_min`, `speed_max`, `speed_std`, 
- `radius_of_gyration`, `distance_sum`
    
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
    
####   `music`
- `music_False`, `music_True`
    
####   `notification`
- `notification_posted`, `notification_removed`
    
####   `orientation`
- `x_min`, `x_max`, `x_mean`, `x_std`
- `y_min`, `y_max`, `y_mean`, `y_std`
- `z_min`, `z_max`, `z_mean`, `z_std`
- `magnitude_min`, `magnitude_max`, `magnitude_mean`, `magnitude_std`
    
####   `pressure`
- `min`, `std`, `min`, `max`
    
####   `proximity`
- `min`, `std`, `min`, `max`
    
####   `relativehumidity`
- `min`, `std`, `min`, `max`
    
####   `ringmode`
- `ringmode_mode_silent`, `ringmode_mode_normal`, `ringmode_mode_vibrate`
    
####   `rotationvector`
- `x_min`, `x_max`, `x_mean`, `x_std`
- `y_min`, `y_max`, `y_mean`, `y_std`
- `z_min`, `z_max`, `z_mean`, `z_std`
- `magnitude_min`, `magnitude_max`, `magnitude_mean`, `magnitude_std`
- `accuracy_min`, `accuracy_max`, `accuracy_mean`, `accuracy_std`
- `scalar_min`, `scalar_max`, `scalar_mean`, `scalar_std`
    
####   `screen`
- `screen_SCREEN_ON`, `screen_SCREEN_OFF`, `screen_episodes_count`, 
- `screen_mean_seconds_per_episode`, `screen_min_seconds_per_episode`, `screen_max_seconds_per_episode`, `screen_std_seconds_per_episode`
    
####   `stepcounter`
- `steps_counter` 
    
####   `stepdetector`
- `steps_detected_count`
    
####   `touch`
- `touch_count` 
    
####   `wifi`
- `is_connected`
    
####   `wifinetworks`
- `wifi_num_of_devices`,
- `wifi_mean_rssi`, `wifi_min_rssi`, `wifi_max_rssi`, `wifi_std_rssi`
 
