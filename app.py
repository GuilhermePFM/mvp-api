
from flask import redirect
from urllib.parse import unquote

from sqlalchemy.exc import IntegrityError

from model import Session, Transaction, User, TransactionType, TransactionCategory
from schemas import TransactionSchema, ErrorSchema, ListTransactionsSchema, show_transaction
from logger import logger
from schemas import *

from apis.users import *
from apis.transactions import *
from config import *


@app.get('/', tags=[home_tag])
def home():
    """Redirects to /openapi to choose the doc style
    """
    return redirect('/openapi')


if __name__ == '__main__':
    app.run()