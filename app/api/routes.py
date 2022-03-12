from flask import Blueprint
from flask_restplus import Api

blueprint = Blueprint(
    'api',
    __name__,
    url_prefix='/api',
)

# API = Api()
# API.init_app(blueprint)
# from . import images,docs
# API.add_namespace(images.api_namespace)
# API.add_namespace(docs.api_namespace)
