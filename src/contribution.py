import os

from pathlib import Path
import pandas as pd
from src.utils.utils import get_logger


def main(input_path: Path, output_path: Path):
    logger.info('Loading users\' contributions...')
    df = pd.read_parquet(input_path)
    for col in ['timestamp']:
        df[col] = pd.to_datetime(df[col], format='%m%d%H%M%S%f')

    # filter out timediary questions
    df = df[df['tag'] == 'time_diary']

    output_path.parent.mkdir(parents=True, exist_ok=True)
    assert len(df) != 0
    if df.index.has_duplicates:
        logger.warning('Reset index, there are duplicates')
        raise ValueError()

    assert (df.groupby(['userid', 'timestamp']).size() == 1).all()
    df.to_csv(output_path, index=False)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='timediary path',
                        default='/Users/munkhdelger/Knowdive/feature-engineering/data/raw/timediary.parquet')
    parser.add_argument('-o', '--output',
                        default='/Users/munkhdelger/Knowdive/feature-engineering/data/interim/timediary.csv')
    parser.add_argument('-l', '--logs', help='path to logging file',
                        default='/Users/munkhdelger/Knowdive/feature-engineering/logs/get_user_label.log')
    args = parser.parse_args()

    logger = get_logger(os.path.basename(__file__), args.logs)

    main(Path(args.input), Path(args.output))
    logger.info("Done!")
