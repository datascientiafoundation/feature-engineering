
# DiversityOne Feature Engineering

Dataset info:

https://datascientiafoundation.github.io/LivePeople-ws/datasets/

## Requirements

- Python 3.9
- Snakemake (for workflow automation)

To install Snakemake, use the following command:

```bash
conda install -c conda-forge snakemake
```

## Installation

Clone the repository

```bash
gh repo clone datascientiafoundation/feature-engineering
```

Create a new environment with [Conda](https://docs.conda.io/en/latest/)

```bash
conda env create -f environment.yml
conda activate feature_env
```

## Repository structure

```
.
├── config/
│   ├── countries.txt        # Contains a list of countries (2-letter country codes).
│   └── datasets.txt         # Contains a list of available datasets.
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

**Download the dataset** and save it in the appropriate folder:
   - If the dataset follows the **flattened structure**(sensors), save it in the `data/raw` folder using the corresponding country’s 2-digit country code (e.g., `data/raw/it/` for Italy).
   - If the dataset follows the **CREP structure** (Hierarchical), save it in the `data/CREP` folder. The datasets in CREP format need to be processed first by the `load_datasets` rule before they can be used for feature extraction.


## Workflow Description
The Snakemake workflow defines rules to process datasets:

**load_datasets**: This rule loads raw datasets from the [CREP](data/CREP) folder into the [raw](data/raw) folder.

    snakemake load_datasets --cores 1

**process_all_features**: This rule processes all datasets found in the [raw](data/raw) folder and outputs the processed features in .csv format to the [processed](data/processed) folder.

    snakemake process_all_features --cores 1

### Configuration Files
**datasets.txt**: Contains a list of available datasets.

**countries.txt**: Contains a list of countries (2-letter country codes).

## Process single dataset

You can process a single dataset using the [src/feature.py](src/feature) script directly:

    python -m src.feature -i data/raw/<COUNTRY>/<SENSOR>.parquet -o data/processed/<COUNTRY>/<SENSOR>.csv -l logs/<COUNTRY>/<SENSOR>.log -t <FREQ>

Example: 

    python -m src.feature -i data/raw/it/accelerometer.parquet -o data/processed/it/accelerometer.csv -l logs/it_accelerometer.log -t 30
