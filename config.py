from flask_openapi3 import OpenAPI, Info, Tag
from flask_cors import CORS

info = Info(title="Finance Control API", version="0.0.1", )
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Docs", 
                description="Go to API doc")

transaction_tag = Tag(name="Transaction", 
                      description="Create and modify transactions")

user_tag = Tag(name="User", 
                description="Create and modify users")

transaction_category_tag = Tag(name="Transaction Category", 
                                description="Create and modify categories")

transaction_type_tag = Tag(name="Transaction Types",
                            description="Create and modifies transaction typees")

classification_model_tag = Tag(name="Classification Model",
                            description="Runs classifier on batch of transactions")
