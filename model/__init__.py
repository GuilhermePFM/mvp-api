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
    
    ml_types = ['Despesa', 'Receita']
    for type in ml_types:
        type = TransactionType(
                                type=type
                                )
        session.add(type)

    user = User(
                email="uncle@bob.com",
                first_name="Bob",
                last_name="Uncle",
            )
    session.add(user)
    user = User(
                email="charlie@bob.com",
                first_name="John",
                last_name="Doe",
            )
    session.add(user)

    ml_categories = ['Presentes', 'Autocuidado - produtos', 'Autocuidado - serviços',
       'Alimentação cotidiana', 'Compras', 'Saúde',
       'Alimentação especial', 'Bares e rolês', 'Entretenimento geral',
       'Viagem ', 'Gui', 'Casa', 'Rendimentos', 'Reembolsos', 'IT',
       'Transporte', 'Trabalho', 'Salário', 'Outros', 'Decoração',
       'Outros Ganhos', 'Educação', 'outros ganhos', 'Ocasiões especiais',
       'Investimento']
    for category in ml_categories:
        category = TransactionCategory(
                                name=category
                                )
        session.add(category)

    transaction = Transaction(
                                value=100,
                                user_id=1,  
                                transaction_type_id=1,  
                                transaction_category_id=1,
                                description="one time purchase"
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
    database_already_exists = database_exists(engine.url)
    if not database_already_exists:
        create_database(engine.url) 

    # cria as tabelas do banco, caso não existam
    Base.metadata.create_all(engine)
    if not database_already_exists:
        populate(Session())

    return Session

Session= init_database()