from flask import Blueprint

blueprint = Blueprint(
    'transporter_blueprint',
    __name__,
    url_prefix='/transporter',
)

