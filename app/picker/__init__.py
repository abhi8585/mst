from flask import Blueprint

blueprint = Blueprint(
    'picker_blueprint',
    __name__,
    url_prefix='/picker',
)

