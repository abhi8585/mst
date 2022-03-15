from flask import Blueprint

blueprint = Blueprint(
    'depo_blueprint',
    __name__,
    url_prefix='/depo',
)

