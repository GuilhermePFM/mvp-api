from model.transaction_category import TransactionCategory
from schemas import ErrorSchema, show_category, TransactionCategorySchema, ListTransactionCategoriesSchema, DeleteTransactionCategorySchema
from config import app
from config import transaction_category_tag as tag 
from model import Session, User
from logger import logger
from sqlalchemy.exc import IntegrityError
from urllib.parse import unquote

@app.post('/transaction_category', tags=[tag],
          responses={"200": TransactionCategorySchema, "409": ErrorSchema, "400": ErrorSchema})
def create_transaction_category(form: TransactionCategorySchema):
    """Create a transaction category"""
    category = TransactionCategory(
        form.category,
       )
    logger.debug(f"Adding transaction category: '{category}'")
    try:
        # criando conexão com a base
        session = Session()
        # adicionando produto
        session.add(category)
        # efetivando o camando de adição de novo item na tabela
        session.commit()
        logger.debug(f"Transaction category successfully added: '{category}'")
        return show_category(category), 200

    except IntegrityError as e:
        error_msg = "Transaction category already exists"
        logger.warning(f"Error adding Transaction category '{category}', {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Could not add Transaction category"
        logger.warning(f"Error adding Transaction category '{category}', {error_msg}")
        return {"mesage": error_msg}, 400

@app.get('/transaction_categories', tags=[tag],
          responses={"200": ListTransactionCategoriesSchema, "409": ErrorSchema, "400": ErrorSchema})
def get_all_transaction_categories():
    """Get all transaction categories"""
    logger.debug(f"Listing all Transaction categories")
   
    session = Session()
    categories = session.query(TransactionCategory).all()

    if not categories:
        return {"users": []}, 200
    else:
        logger.debug(f"{len(categories)} types found")
        return [show_category(cat) for cat in categories], 200

@app.delete('/transaction_category', tags=[tag],
            responses={"200": DeleteTransactionCategorySchema, "404": ErrorSchema})
def delete_category(query: TransactionCategorySchema) -> tuple[dict[str, str], int]:
    """Deletes a category given name

    Return a confirmation message
    """
    category = unquote(unquote(query.category))
    logger.debug(f"Deleting Category {category}")
    session = Session()
    count = session.query(TransactionCategory).filter(TransactionCategory.name == category).delete()
    session.commit()

    if count > 0:
        logger.debug(f"Category #{category} deleted")
        return {"mesage": "Category removed successfully", "category": category}, 200
    else:
        error_msg = "Category not found"
        logger.warning(f"Error removing category '{category}', {error_msg}")
        return {"mesage": error_msg}, 404