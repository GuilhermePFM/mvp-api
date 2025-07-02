from pytest import fixture
import pandas as pd
from security.dataset import encrypt_dataset, decrypt_dataset
from security.symmetric.utils import generate_key


@fixture(scope="session")
def df():
    return pd.DataFrame({
    'a': ['1', '2', '3'],
    'b': [4.0, 5.5, 6.1],
    'teste com espaço': [4, 5, 6],
})


@fixture(scope="session")
def MASTER_KEY():
    return generate_key()


@fixture(scope="session")
def encrypted_data(df, MASTER_KEY):
    return encrypt_dataset(df, MASTER_KEY)


def test_encrypt_dataset(df, encrypted_data):
    encrypted_df, dtypes = encrypted_data
    assert not encrypted_df.equals(df)


def test_decrypt_dataset(df, encrypted_data, MASTER_KEY):
    encrypted_df, dtypes = encrypted_data
    decrypted_df = decrypt_dataset(encrypted_df, MASTER_KEY, dtypes)
    assert decrypted_df.equals(df)
