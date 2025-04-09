import os
from src.utils.utils import get_logger
import shutil
from pathlib import Path


def isPaquet(path) -> bool:
    fname = os.path.dirname(path)
    if "parquet" in fname:
        return True
    return False


def main(path_to_crep: Path, path_to_raw: Path):
    site_dirs = [p for p in path_to_crep.rglob("*") if p.is_dir() and p.name.startswith("Site")]
    print(f"Number of 'Site' directories: {len(site_dirs)}")

    for site_dir in site_dirs:
        sensors = [p for p in site_dir.rglob("*") if str(p.absolute()).count('parquet') == 1 and p.name.endswith(".parquet")]
        country = site_dir.name.split("_")[-1].lower()
        if len(sensors) == 0:
            logger.info(f"skipped {site_dir}")
            continue

        for sensor in sensors:
            dest_path = path_to_raw / country / sensor.name
            try:
                # If it's a directory, use copytree
                if sensor.is_dir():
                    shutil.copytree(sensor, dest_path)
                    logger.info(f'Directory copied: {sensor} --> {dest_path}')
                # If it's a file, use copy2
                elif sensor.is_file():
                    shutil.copy2(sensor, dest_path)
                    logger.info(f'File copied: {sensor} --> {dest_path}')
                else:
                    logger.warning(f"Skipping unknown type: {sensor}")
            except FileExistsError:
                logger.info(f"file exist: {dest_path}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default = '/Users/munkhdelger/Knowdive/feature-engineering/data/CREP')
    parser.add_argument('-o', '--output', default = '/Users/munkhdelger/Knowdive/feature-engineering/data/raw')
    parser.add_argument('-l', '--logs', default = '/Users/munkhdelger/Knowdive/feature-engineering/logs/load.log')
    args = parser.parse_args()

    logger = get_logger(os.path.basename(__file__), args.logs)

    main(Path(args.input), Path(args.output))

