from flask import Blueprint

blueprint = Blueprint(
    'testing_blueprint',
    __name__,
    url_prefix='/testing',
)

