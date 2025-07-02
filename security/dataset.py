import pandas as pd 
from security.symmetric.utils import encrypt_val, decrypt_val, encrypt_file, read_decrypted_file


def encrypt_dataset(dataset:pd.DataFrame, MASTER_KEY):
    encrypted_dataset = dataset.copy()
    for column in encrypted_dataset.columns:
        encrypted_dataset[column] = encrypted_dataset[column].apply(lambda x: encrypt_val(str(x),MASTER_KEY))
    return encrypted_dataset, dataset.dtypes


def decrypt_dataset(encrypted_dataset:pd.DataFrame,MASTER_KEY, dtypes:dict):
    decrypted_dataset = encrypted_dataset.copy()
    for column in decrypted_dataset.columns:
        decrypted_dataset[column] = decrypted_dataset[column].apply(lambda x: decrypt_val(x,MASTER_KEY))

    return decrypted_dataset.astype(dtypes)