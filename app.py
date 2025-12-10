
from flask import redirect
from urllib.parse import unquote

from sqlalchemy.exc import IntegrityError

from model import Session, Transaction, User, TransactionType, TransactionCategory
from schemas import TransactionSchema, ErrorSchema, ListTransactionsSchema, show_transaction
from logger import logger
from schemas import *

from apis.users import *
from apis.transactions import *
from apis.transactions_type import *
from apis.transactions_category import *
from apis.batch_classifier import *
from config import *


@app.get('/', tags=[home_tag])
def home():
    """Redirects to /openapi to choose the doc style
    """
    return redirect('/openapi')


if __name__ == '__main__':
    print("running on 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)