from sklearn.compose import ColumnTransformer, make_column_transformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import (
    StandardScaler,
    Normalizer,
)
from sklearn.preprocessing import FunctionTransformer
from sklearn.pipeline import FeatureUnion
from machine_learning.transactions_classification.lib.feature_engineering import add_keyword_hints, add_date_features, NUMERIC_FEATURES, DATE_FEATURES, TEXT_FEATURES
from machine_learning.transactions_classification.lib.tokenization import hidden_state_from_text_inputs, tokenized_pytorch_tensors


VERBOSE = False


def description_transformer():
    return make_pipeline(
        FunctionTransformer(tokenized_pytorch_tensors, kw_args={"column_list": ["input_ids", "attention_mask"]}),
        FunctionTransformer(hidden_state_from_text_inputs),
        verbose=VERBOSE
    )


def new_feature_hints_transformer():
    return make_pipeline(
        FunctionTransformer(add_keyword_hints),
        Normalizer(),
        verbose=VERBOSE
    )

def text_transformer():
    estimators = [
        ('description', description_transformer()), 
        ('keyword_hints', new_feature_hints_transformer())]
    
    combined = FeatureUnion(estimators, verbose=VERBOSE)
    return combined


def date_transformer():
    return make_pipeline( FunctionTransformer(add_date_features),
                          Normalizer(),
                          verbose=VERBOSE
    )

def get_preprocessing_transformer(VERBOSE=False ) -> ColumnTransformer:
    preprocessor = make_column_transformer(
                    ( StandardScaler(), NUMERIC_FEATURES),
                    ( date_transformer(), DATE_FEATURES),
                    ( text_transformer(), TEXT_FEATURES),
        remainder='passthrough', verbose=VERBOSE)
    return preprocessor 