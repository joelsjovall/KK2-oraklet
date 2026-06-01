from io import BytesIO

import pandas as pd


_dataset: pd.DataFrame | None = None


def save_dataset(dataframe: pd.DataFrame) -> None:
    global _dataset
    _dataset = dataframe


def get_dataset() -> pd.DataFrame | None:
    return _dataset


def has_dataset() -> bool:
    return _dataset is not None


def clear_dataset() -> None:
    global _dataset
    _dataset = None


def create_stats() -> dict:
    if _dataset is None:
        return {}

    stats = _dataset.describe()
    stats = stats.where(pd.notna(stats), None)
    return stats.to_dict()


def read_csv_file(file_content: bytes) -> pd.DataFrame:
    return pd.read_csv(BytesIO(file_content))
