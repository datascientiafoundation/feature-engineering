from pathlib import Path

from snakemake.io import expand


files_to_ignore = ['survey',
                   'timediary']

configfile: "config/config.yaml"

sensors = config['datasets']

sensors = [ds for ds in sensors if ds not in files_to_ignore]

rule process_timediary:
    input:
        "data/raw/timediary.parquet"
    output:
        "data/interim/timediary.csv"
    log:
        "logs/contribution.log"
    shell:
        "python -m src.contribution -i {input} -o {output} -l {log}"


rule process_feature:
    input:
        input_sensor="data/raw/{ds}.parquet",
        timediary="data/interim/timediary.csv"  # timediary input
    output:
        "data/interim/{ds}.csv"
    log:
        "logs/{ds}.log"
    params:
        freq=config['freq'],
        timediary_include = config['timediary']
    shell:
        "python -m src.feature -i {input.input_sensor} -t {input.timediary} -o {output} -l {log} -f {params.freq} -ti {params.timediary_include}"


rule join_features:
    input:
        expand("data/interim/{ds}.csv", ds=sensors),
    output:
        "data/processed/joined_features.csv"
    log:
        "logs/join_features.log"
    shell:
        "python -m src.join_features -i {input} -o {output} -l {log}"


rule all:
    input:
        "data/processed/joined_features.csv"
