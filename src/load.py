import os
from src.utils.utils import get_logger
import shutil
from pathlib import Path


def isPaquet(path) -> bool:
    fname = os.path.dirname(path)
    if "parquet" in fname:
        return True
    return False


def main(input_path: Path, path_to_raw: Path):
    sensors = [p for p in input_path.rglob("*") if str(p.absolute()).count('parquet') == 1 and p.name.endswith(".parquet")]
    if len(sensors) == 0:
        logger.info(f"skipped {input_path}")
        return

    for sensor in sensors:
        dest_path = path_to_raw / sensor.name
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
    parser.add_argument('-i', '--input')
    parser.add_argument('-o', '--output')
    parser.add_argument('-l', '--logs')
    args = parser.parse_args()

    logger = get_logger(os.path.basename(__file__), args.logs)

    main(Path(args.input), Path(args.output))

