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
                shutil.copytree(sensor, dest_path)
                file_size = sum(
                    os.path.getsize(os.path.join(dest_path, f)) for f in os.listdir(dest_path) if os.path.isfile(os.path.join(dest_path, f)))
                logger.info(f'Destination file size: {file_size} bytes')
                logger.info(f'file copied: {sensor} --> {dest_path}')
            except FileExistsError:
                logger.info(f"file exist: {dest_path}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input')
    parser.add_argument('-o', '--output')
    parser.add_argument('-l', '--logs')
    args = parser.parse_args()

    logger = get_logger(os.path.basename(__file__), args.logs)

    main(Path(args.input), Path(args.output))

