from flask import Blueprint

blueprint = Blueprint(
    'audit_blueprint',
    __name__,
    url_prefix='/audit',
)

