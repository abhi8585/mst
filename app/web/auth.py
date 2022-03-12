from app.web import blueprint
from flask_restful import Resource, Api
import json

from app.models import gallery,package, packagecategory, user, role, usertorole, image, imagetogallery, userinfo


@blueprint.route('/bye')
def bye():
    data = userinfo.query.all()
    user_names = [user.name for user in data]
    return json.dumps(user_names)