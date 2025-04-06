from typing import Literal
from schemas import UserSchema, ErrorSchema, show_user, SearchUserSchema, ListUserSchema, DeleteUserSchema
from config import app
from config import user_tag as tag 
from model import Session, User
from logger import logger
from sqlalchemy.exc import IntegrityError
from urllib.parse import unquote


@app.post('/user', tags=[tag],
          responses={"200": UserSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_user(form: UserSchema):
    """
    Add a new user
    """
    user = User(
        first_name=form.first_name,
        last_name=form.last_name,
        email=form.email)
    logger.debug(f"Adicionando user: '{user}'")

    try:
        with Session() as session:
            session.add(user)
            session.commit()
            logger.debug(f"User successfully added: '{user}'")
            return show_user(user), 200

    except IntegrityError as e:
        error_msg = "User already exists"
        logger.warning(f"Error adding user '{user}', {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e:
        error_msg = "Could not add user"
        logger.warning(f"Error adding user '{user}', {error_msg}")
        return {"mesage": error_msg}, 400


@app.get('/user', tags=[tag],
          responses={"200": UserSchema, "409": ErrorSchema, "400": ErrorSchema})
def get_user(query: SearchUserSchema):
    """
    Get user by email
    """
    email = query.email
    logger.debug(f"Coletando dados sobre user #{email}")
    with Session() as session:
        user = session.query(User).filter(User.email == email).first()

        if not user:
            error_msg = f"User {email} not found"
            logger.warning(f"Error searching for user '{email}', {error_msg}")
            return {"mesage": error_msg}, 404
        else:
            logger.debug(f"User found: '{user.email}'")
            return show_user(user), 200

@app.get('/users', tags=[tag],
          responses={"200": ListUserSchema, "409": ErrorSchema, "400": ErrorSchema})
def get_all_users() -> tuple[dict[str, list], int]:
    """
    Lists all users
    """
    logger.debug(f"Listing all users")
   
    with Session() as session:
        users = session.query(User).all()

        if not users:
            return {"users": []}, 200
        else:
            logger.debug(f"{len(users)} users found")
            return [show_user(user) for user in users], 200

def removed_succesfully(count):
    return count > 0

@app.delete('/user', tags=[tag],
            responses={"200": DeleteUserSchema, "404": ErrorSchema})
def delete_user(query: SearchUserSchema) -> tuple[dict[str, str], int]:
    """Deletes a User given email

    Return a confirmation message
    """
    email = unquote(unquote(query.email))
    logger.debug(f"Deleting User {email}")
    with Session() as session:
        session = Session()
        count = session.query(User).filter(User.email == email).delete()
        session.commit()

        if removed_succesfully(count):
            logger.debug(f"User #{email} deleted")
            return {"mesage": "User removed successfully", "email": email}, 200
        else:
            error_msg = "User not found"
            logger.warning(f"Error deleting user '{email}', {error_msg}")
            return {"mesage": error_msg}, 404