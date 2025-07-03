from machine_learning.transactions_classifier import TransactionsClassifier
# import TransactionsClassifier
from pytest import fixture
from sklearn.base import BaseEstimator, ClassifierMixin
import numpy as np
import os
from pathlib import Path
import pickle
from sklearn.metrics import balanced_accuracy_score
from machine_learning.utils import load_pickle


@fixture
def fixtures_path():
    return Path(os.path.dirname(__file__)) / "classification_fixtures"


def test_model_average_accuracy(classifier_model: TransactionsClassifier, X_test, balanced_accuracy_score_result, y_encoder, y_test, test_seed):
    #TODO
    assert True

