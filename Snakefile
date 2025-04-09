from pathlib import Path

from snakemake.io import expand

files_to_ignore = ['contributlionanswers',
                   'timediariesconfirmation',
                   'contributionquestions',
                   'tasksconfirmation',
                   'timediaries',
                   'location_poi',
                   'survey',
                   'timediary']

with open("config/datasets.txt") as f:
    DATASETS = [line.strip() for line in f if line.strip()]
with open("config/countries.txt") as f:
    countries = [line.strip() for line in f if line.strip()]

filtered_datasets = [ds for ds in DATASETS if ds not in files_to_ignore]


rule load_datasets:
    input:
        crep="data/CREP",
        raw="data/raw"
    log:
        "logs/load.log"
    shell:
        "python -m src.load -i {input.crep} -o {input.raw} -l {log}"


rule process_feature:
    input:
        "data/raw/{country}/{ds}.parquet"
    output:
        "data/processed/{country}/{ds}.csv"
    log:
        "logs/{country}_{ds}.log"
    params:
        freq=30
    shell:
        "python -m src.feature -i {input} -o {output} -l {log} -t {params.freq}"


rule process_all_features:
    input:
        expand("data/processed/{country}/{ds}.csv", country=countries, ds=filtered_datasets)
