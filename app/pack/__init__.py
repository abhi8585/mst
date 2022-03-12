from flask import Blueprint

blueprint = Blueprint(
    'pack_blueprint',
    __name__,
    url_prefix='/pack',
    template_folder='templates',
    static_folder='static'
)

