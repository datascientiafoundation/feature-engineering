
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
│   ├── config.yaml        # Contains a list of countries and sensors 
├── data/
│   ├── CREP/                # Datasets following the CREP structure (Hierarchical).
│   ├── raw/                 # Raw datasets, organized by country code.
│   └── processed/           # Processed datasets with engineered features.
├── logs/
├── src/
│   ├── utils/
│       ├── appcategories.csv  # Contains mapping or metadata related to application categories used in the datasets.
│       ├── utils.py           # Utility functions for the project.
│   ├── feature.py           # Script for performing feature engineering on a single dataset.
│   └── load.py              # Script for loading and potentially transforming CREP datasets.
├── CITATION.cff
├── environment.yml          # Conda environment configuration file.
├── LICENCE                  # Contains the license information for the project (e.g., MIT License).
├── README.md
└── Snakefile                # Defines the workflow for processing datasets.

```

## Data preparation

Download the dataset (the datasets can be requested on the [Datascientia platform](https://ds.datascientia.eu/marketplace/welcome)) and save it in the appropriate folder:
   
   - If the dataset follows the **flattened structure**, save it in the `data/raw` folder.
   
   - If the dataset follows the **Hierarchical structure**, save it in the `data/CREP` folder. The datasets in CREP format need to be flattened first by following script:

```bash
 python -m src.load -i data/CREP -o data/raw -l logs/load.log
```


## Workflow Description

The Snakemake workflow defines rules to process datasets. The workflow assumes that all datasets are located in the [raw](data/raw) folder. It is designed to run all sensors at once.

```bash
snakemake all --cores 1
```

This rule processes all datasets found in the [raw](data/raw) folder and outputs the processed features in .csv format to the [processed](data/processed) folder.


### Configuration

**config.yaml**: Contains a list of available datasets. The names are strict; therefore, sensors defined here will be processed only if the corresponding dataset is available.

## Process single dataset

You can process a single dataset using the [src/feature.py](src/feature) script directly:
```bash
python -m src.feature -i data/raw/<SENSOR>.parquet -o data/processed/<SENSOR>.csv -l logs/<SENSOR>.log -t <FREQ>
```
Example: 
```bash
python -m src.feature -i data/raw/accelerometer.parquet -o data/processed/accelerometer.csv -l logs/accelerometer.log -t 30
```

## Supported Datasets

The following sensor datasets are currently supported for feature extraction:

-   `accelerometer`
   
-   `accelerometeruncalibrated`
    
-   `activities`
    
-   `airplanemode`
    
-   `ambienttemperature`
    
-   `applications`
    
-   `batterycharge`
    
-   `batterylevel`
    
-   `bluetooth`
    
-   `cellularnetwork`
    
-   `doze`
    
-   `geomagneticrotationvector`
    
-   `gravity`
    
-   `gyroscope`
    
-   `gyroscopeuncalibrated`
    
-   `headsetplug`
    
-   `light`
    
-   `linearacceleration`
    
-   `location`
    
-   `magneticfield`
    
-   `magneticfielduncalibrated`
    
-   `music`
    
-   `notification`
    
-   `orientation`
    
-   `pressure`
    
-   `proximity`
    
-   `relativehumidity`
    
-   `ringmode`
    
-   `rotationvector`
    
-   `screen`
    
-   `stepcounter`
    
-   `stepdetector`
    
-   `touch`
    
-   `wifi`
    
-   `wifinetworks`