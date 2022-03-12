from flask import Blueprint

blueprint = Blueprint(
    'User_blueprint',
    __name__,
    url_prefix='/users',
    template_folder='templates',
    static_folder='static'
)

