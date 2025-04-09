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

configfile: "config/config.yaml"


sensors = config['datasets']
countries = config['countries']

print(sensors)
print(countries)

# ignoring non-sensor datasets
sensors = [ds for ds in sensors if ds not in files_to_ignore]

# Get countries with raw data available
existing_countries = []
for country in countries:
    country_data_path = Path(f"data/raw/{country}")
    if country_data_path.exists():
        existing_countries.append(country)

# Get sensors available
existing_sensors = []
for country in existing_countries:
    for sensor in sensors:
        path = Path(f"data/raw/{country}/{sensor}.parquet")
        if path.exists():
            existing_sensors.append(sensor)


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


rule all:
    input:
        expand("data/processed/{country}/{ds}.csv",country=existing_countries,ds=existing_sensors)


