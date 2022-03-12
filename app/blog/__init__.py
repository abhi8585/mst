from flask import Blueprint

blueprint = Blueprint(
    'blog_blueprint',
    __name__,
    url_prefix='/blog',
    template_folder='templates',
    static_folder='static'
)

