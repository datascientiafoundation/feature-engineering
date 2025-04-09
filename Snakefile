from pathlib import Path

from snakemake.io import expand


files_to_ignore = ['survey',
                   'timediary']

configfile: "config/config.yaml"


sensors = config['datasets']

sensors = [ds for ds in sensors if ds not in files_to_ignore]

rule process_feature:
    input:
        "data/raw/{ds}.parquet"
    output:
        "data/processed/{ds}.csv"
    log:
        "logs/{ds}.log"
    params:
        freq=30
    shell:
        "python -m src.feature -i {input} -o {output} -l {log} -t {params.freq}"


rule all:
    input:
        expand("data/processed/{ds}.csv", ds=sensors)


