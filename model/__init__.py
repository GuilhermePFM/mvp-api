from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

# importando os elementos definidos no modelo
from model.base import Base
from model.user import User
from model.transaction_category import TransactionCategory
from model.transaction_type import TransactionType
from model.transaction import Transaction
from pathlib import Path


DB_PATH = "database/"
DB_URL = f'sqlite:///{DB_PATH}/db.sqlite3'

def create_database_dir(dirname:str, clean=False):
    dirpath = Path(dirname)
    
    if clean:
        if dirpath.exists():
            os.rmdir(dirpath)
        os.makedirs(dirpath)

    elif not dirpath.exists():
        os.makedirs(dirpath)

def populate(session):
    user = User(
                email="teste@email.com",
                first_name="Teste User",
                last_name="Last Name",
            )
    session.add(user)
    category = TransactionCategory(
                                name="Casa"
                                )
    session.add(category)
    ttype = TransactionType(
                                type="Despesa"
                            )
    session.add(ttype)

    transaction = Transaction(
                                value=100,
                                user_id=1,  
                                transaction_type_id=1,  
                                transaction_category_id=1
                            )
    session.add(transaction)
    session.commit()

def init_database():
    # Verifica se o diretorio não existe
    if not os.path.exists(DB_PATH):
        # então cria o diretorio
        os.makedirs(DB_PATH)

    create_database_dir(DB_PATH)

    # cria a engine de conexão com o banco
    engine = create_engine(DB_URL, echo=False)

    # Instancia um criador de seção com o banco
    Session = sessionmaker(bind=engine)

    # cria o banco se ele não existir 
    if not database_exists(engine.url):
        create_database(engine.url) 

    # cria as tabelas do banco, caso não existam
    Base.metadata.create_all(engine)
    populate(Session())

    return Session

Session= init_database()