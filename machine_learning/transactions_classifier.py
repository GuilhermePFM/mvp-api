from abc import ABC
import os
from pathlib import Path
import pickle
from logging import getLogger
from typing import Protocol, Optional
from machine_learning.utils import load_joblib, load_pickle


MODEL_REPOSITORY_PATH = Path(os.getenv("MODEL_PATH", os.path.dirname(__file__))) / "transactions_classification" / 'models'


# Define a protocol for scikit-learn models that are both classifiers and base estimators
class SklearnClassifierProtocol(Protocol):
    """
    A protocol representing scikit-learn compatible models
    that are both BaseEstimator and ClassifierMixin.
    This means instances are expected to have methods/attributes
    from both parent classes (e.g., predict, score, get_params, set_params).
    """
    def fit(self, X) -> None:
        pass
    def predict(self, X) -> None:
        pass


class SklearnTransformerProtocol(Protocol):
    """
    A protocol representing scikit-learn Transformer compatible models
    """
    def transform(self, X) -> None:
        pass

    def validate(self, X) -> bool:
        return False


class MLModel(ABC):
    """
    Abstract base class for machine learning models.
    """

    def __init__(self, model_path: Path, preprocessor_path: Path):
        self.model_path = model_path
        self.preprocessor_path = preprocessor_path
        self.model: Optional[SklearnClassifierProtocol] = None
        self.preprocessor: Optional[SklearnTransformerProtocol] = None
        self.is_loaded = False
        if (not self.is_loaded) and self.model_path.exists():
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
            self.model = load_pickle(self.model_path)
            self.preprocessor = load_joblib(self.preprocessor_path)
            self.is_loaded = True
            getLogger(self.__class__.__name__).info(f"Model loaded successfully from {self.model_path}")
        except pickle.UnpicklingError as e:
            getLogger(self.__class__.__name__).error(f"Error unpickling model from {self.model_path}: {e}")
            self.model = None
            self.is_loaded = False
        except Exception as e:
            getLogger(self.__class__.__name__).error(f"Model could not be loaded from {self.model_path}: {e}")
            self.is_loaded = False

    def predict(self, X):
        """
        Predict labels for the provided features.
        """
        self.load()
        if self.needs_preprocessing(X):
            X = self.preprocess(X)

        if not self.is_loaded or self.model is None:
            message = "Model is not loaded. Call load() first."
            getLogger(self.__class__.__name__).error(message)
            raise RuntimeError(message)
        
        return self.model.predict(X)    

    def needs_preprocessing(self, X) -> bool:
        """
        Check if the input data needs preprocessing.
        This can be overridden by subclasses if needed.
        """
        return X.shape[1] == 3 if self.preprocessor else False
    
    def preprocess(self, X):
        """
        Preprocess the inputs for prediction.
        """
        if not self.is_loaded or self.preprocessor is None:
            message = "Model is not loaded. Call load() first."
            getLogger(self.__class__.__name__).error(message)
            raise RuntimeError(message)
        
        X= X.rename(columns = {"value":'Valor', "date": 'Data', "description":'Descrição'})
        
        return self.preprocessor.transform(X)


class TransactionsClassifier(MLModel):
    """
    Classifier for transaction data.
    """

    def __init__(self, repository_path: Path = MODEL_REPOSITORY_PATH):
        self.model_file_name: str = "classification_model.pkl"
        self.preprocessor_file_name: str = "classification_preprocessor.pkl"
        self.repository_path: Path = repository_path
        model_path = repository_path / self.model_file_name
        preprocessor_path = repository_path.parent / "pipelines" / self.preprocessor_file_name
        super().__init__(model_path, preprocessor_path)