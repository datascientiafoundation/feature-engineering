from pathlib import Path

files_to_ignore = [
    'activitiesperlabel.parquet',
    'contributlionanswers.parquet',
    'timediariesconfirmation.parquet',
    'contributionquestions.parquet',
    'tasksconfirmation.parquet',
    'timediaries.parquet',
    'locationeventpertime_poi.parquet'
]

def get_existing_datasets():
    dataset_list = []
    for path in Path("data/raw").rglob("*.parquet"):
        if (
            str(path.absolute()).count('parquet') == 1
            and path.name.endswith(".parquet")
            and path.name not in files_to_ignore
        ):
            country = path.parent.name
            ds = path.stem
            print(f"Found: {path}")  # helpful debug
            dataset_list.append((country, ds))
    return dataset_list

if __name__ == "__main__":
    print(get_existing_datasets())
