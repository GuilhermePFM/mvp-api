import pickle
from pathlib import Path
import joblib
from typing import Any
from machine_learning.transactions_classification.lib import feature_engineering


def load_pickle(path) -> Any:
    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data


def load_joblib(path:Path) -> Any:
    with open(path, 'rb') as f:
        data = joblib.load(f)
    return data