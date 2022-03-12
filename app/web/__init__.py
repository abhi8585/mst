from flask import Blueprint

blueprint = Blueprint(
    'web_blueprint',
    __name__,
    url_prefix='/web',
)

