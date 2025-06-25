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


@fixture
def test_seed():
    return 1


@fixture
def classifier_model():
    return TransactionsClassifier()


@fixture
def X_test(fixtures_path):
    return load_pickle(fixtures_path / "X_test_preprocessed.pkl")


@fixture
def y_test(fixtures_path):
    return load_pickle(fixtures_path/ "y_test_encoded.pkl")


@fixture
def y_predicted(fixtures_path, test_seed):
    return load_pickle(fixtures_path/ f"y_predictions_seed_{test_seed}.pkl")


@fixture
def balanced_accuracy_score_result(fixtures_path, test_seed):
    return load_pickle(fixtures_path/ f"balanced_accuracy_score_seed_{test_seed}.pkl")
  

@fixture
def y_encoder(fixtures_path):
    return load_pickle(fixtures_path/ "y_encoder.pkl")


def test_model_average_accuracy(classifier_model: TransactionsClassifier, X_test, balanced_accuracy_score_result, y_encoder, y_test, test_seed):
    classifier_model.load()
    np.random.seed(test_seed)
    y_pred_model = classifier_model.predict(X_test)
    score = balanced_accuracy_score(y_test, y_encoder.transform(y_pred_model))
    assert np.isclose(score, balanced_accuracy_score_result), "Accuracy score should match."

