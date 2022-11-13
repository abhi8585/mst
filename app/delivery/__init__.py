from flask import Blueprint

blueprint = Blueprint(
    'delivery',
    __name__,
    url_prefix='/delivery',
    template_folder='templates',
    static_folder='static'
)

