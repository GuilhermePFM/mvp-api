from abc import ABC
import os
from pathlib import Path
import pickle
from logging import getLogger
from typing import Union
from typing import ClassVar
from typing import Protocol, Optional


MODEL_REPOSITORY_PATH = Path(os.getenv("MODEL_PATH", os.path.dirname(__file__)))


# Define a protocol for scikit-learn models that are both classifiers and base estimators
class SklearnClassifierProtocol(Protocol):
    """
    A protocol representing scikit-learn compatible models
    that are both BaseEstimator and ClassifierMixin.
    This means instances are expected to have methods/attributes
    from both parent classes (e.g., predict, score, get_params, set_params).
    """
    def fit(self) -> None:
        pass
    def predict(self, X) -> None:
        pass


class MLModel(ABC):
    """
    Abstract base class for machine learning models.
    """

    def __init__(self, model_path: Path):
        self.model_path = model_path
        self.model: Optional[SklearnClassifierProtocol] = None
        self.is_loaded = False
        if self.is_loaded and self.model_path.exists():
            self.load()

    def train(self, X, y):
        """
        Train the model with the provided features and labels.
        """
        raise NotImplementedError("Train method must be implemented by subclasses.")
    
    def load(self):
        """
        Load a pre-trained model from the specified path.
        """
        if self.is_loaded:
            getLogger(self.__class__.__name__).info(f"Model already loaded from {self.model_path}")
            return
        
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            self.is_loaded = True
            getLogger(self.__class__.__name__).info(f"Model loaded successfully from {self.model_path}")
        except pickle.UnpicklingError as e:
            getLogger(self.__class__.__name__).error(f"Error unpickling model from {self.model_path}: {e}")
            self.model = None
            self.is_loaded = False
        except Exception as e:
            getLogger(self.__class__.__name__).error(f"Model could not be loaded from {self.model_path}: {e}")
            self.model = None
            self.is_loaded = False

    def predict(self, X):
        """
        Predict labels for the provided features.
        """
        if not self.is_loaded or self.model is None:
            message = "Model is not loaded. Call load() first."
            getLogger(self.__class__.__name__).error(message)
            raise RuntimeError(message)
        
        return self.model.predict(X)    


class TransactionsClassifier(MLModel):
    """
    Classifier for transaction data.
    """

    def __init__(self, model_path: Path=MODEL_REPOSITORY_PATH):
        self.model_file_name: str = "classification_model.pkl"
        super().__init__(model_path / self.model_file_name)