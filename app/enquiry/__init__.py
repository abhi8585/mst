from flask import Blueprint

blueprint = Blueprint(
    'enquiry_blueprint',
    __name__,
    url_prefix='/enquiry',
    template_folder='templates',
    static_folder='static'
)

