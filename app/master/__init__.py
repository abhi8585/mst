from flask import Blueprint

blueprint = Blueprint(
    'master_blueprint',
    __name__,
    url_prefix='/master',
    template_folder='templates',
    static_folder='static'
)

