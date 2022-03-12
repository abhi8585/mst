from flask import Blueprint

blueprint = Blueprint(
    'category_blueprint',
    __name__,
    url_prefix='/category',
    template_folder='templates',
    static_folder='static'
)

