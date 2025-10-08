import os

from pathlib import Path
import pandas as pd
from pandas.core.dtypes.common import is_datetime64_any_dtype

from src.utils.utils import get_logger


def main(input_path: Path, output_path: Path, tag: str):
    logger.info('Loading users\' contributions...')
    df = pd.read_parquet(input_path)
    for col in ['instancetimestamp', 'answertimestamp', 'notificationtimestamp']:
        if not is_datetime64_any_dtype(df[col]):
            raise TypeError(f'column {col} is not a datetime64 dtype')

    # filter out timediary questions
    df = df[df['tag'] == tag]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    assert len(df) != 0
    if df.index.has_duplicates:
        logger.warning('Reset index, there are duplicates')
        raise ValueError()

    assert (df.groupby(['userid', 'instancetimestamp']).size() == 1).all()
    df.to_csv(output_path, index=False)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='timediary path',
                        default='./data/raw/timediary.parquet')
    parser.add_argument('-o', '--output',
                        default='./data/interim/timediary.csv')
    parser.add_argument('-l', '--logs', help='path to logging file',
                        default='./logs/get_user_label.log')
    parser.add_argument('-t', '--tag', help='tag value, e.g., "Time Diaries"', default='tag')
    args = parser.parse_args()

    logger = get_logger(os.path.basename(__file__), args.logs)

    main(Path(args.input), Path(args.output), args.tag)
    logger.info("Done!")
