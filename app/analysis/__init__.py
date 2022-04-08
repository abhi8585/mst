from flask import Blueprint

blueprint = Blueprint(
    'analysis_blueprint',
    __name__,
    url_prefix='/analysis',
    template_folder='templates',
    static_folder='static'
)

