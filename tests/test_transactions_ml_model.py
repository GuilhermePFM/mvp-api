from machine_learning_models.transactions_classifier import TransactionsClassifier
# import TransactionsClassifier
from pytest import fixture
from sklearn.base import BaseEstimator, ClassifierMixin
import numpy as np
import os
from pathlib import Path
import pickle
from sklearn.metrics import balanced_accuracy_score


@fixture
def fixtures_path():
    return Path(os.path.dirname(__file__)) / "classification_fixtures"


@fixture
def test_seed():
    return 1


@fixture
def classifier_model():
    return TransactionsClassifier()


def test_loading_model(classifier_model: TransactionsClassifier ):
    classifier_model.load()
    assert (classifier_model.is_loaded is True) and (classifier_model.model is not None), "Model should be loaded successfully."


def test_loaded_model_type(classifier_model: TransactionsClassifier):
    classifier_model.load()
    assert (isinstance(classifier_model.model, BaseEstimator) and isinstance(classifier_model.model, ClassifierMixin)), "Model should be of type BaseEstimator and ClassifierMixin."


def load_pickle(path):
    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data


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


def test_predicting_with_model(classifier_model: TransactionsClassifier, X_test, y_predicted, test_seed):
    classifier_model.load()
    np.random.seed(test_seed)
    y_pred_model = classifier_model.predict(X_test)
    assert np.all(y_pred_model== y_predicted), "Predicted labels should match the expected labels."
   

@fixture
def y_encoder(fixtures_path):
    return load_pickle(fixtures_path/ "y_encoder.pkl")


def test_model_average_accuracy(classifier_model: TransactionsClassifier, X_test, balanced_accuracy_score_result, y_encoder, y_test, test_seed):
    classifier_model.load()
    np.random.seed(test_seed)
    y_pred_model = classifier_model.predict(X_test)
    score = balanced_accuracy_score(y_test, y_encoder.transform(y_pred_model))
    assert np.isclose(score, balanced_accuracy_score_result), "Accuracy score should match."


def test_model_training():
    assert True