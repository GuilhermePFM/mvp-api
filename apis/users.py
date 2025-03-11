from schemas import UserSchema, ErrorSchema, show_user, SearchUserSchema, ListUserSchema
from config import app
from config import user_tag as tag 
from model import Session, User
from logger import logger
from sqlalchemy.exc import IntegrityError


@app.post('/user', tags=[tag],
          responses={"200": UserSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_user(form: UserSchema):
    user = User(
        first_name=form.first_name,
        last_name=form.last_name,
        email=form.email)
    logger.debug(f"Adicionando user: '{user}'")
    try:
        # criando conexão com a base
        session = Session()
        # adicionando produto
        session.add(user)
        # efetivando o camando de adição de novo item na tabela
        session.commit()
        logger.debug(f"User successfully added: '{user}'")
        return show_user(user), 200

    except IntegrityError as e:
        error_msg = "User already exists"
        logger.warning(f"Error adding user '{user}', {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Could not add user"
        logger.warning(f"Error adding user '{user}', {error_msg}")
        return {"mesage": error_msg}, 400


@app.get('/user', tags=[tag],
          responses={"200": UserSchema, "409": ErrorSchema, "400": ErrorSchema})
def get_user(query: SearchUserSchema):
    email = query.email
    logger.debug(f"Coletando dados sobre user #{email}")
    session = Session()
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
def get_all_users():
    logger.debug(f"Listing all users")
   
    session = Session()
    users = session.query(User).all()

    if not users:
        return {"users": []}, 200
    else:
        logger.debug(f"{len(users)} users found")
        return [show_user(user) for user in users], 200