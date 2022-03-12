from email import message
from app.web import blueprint
from flask_restful import Resource, Api
from flask import jsonify, render_template, redirect, request, url_for
import json
from app.base.util import verify_pass

from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)

from app.models import role, usertorole, userinfo, disttovendor, distvendor, sku
from app.base.models import User

# helper function to get the distributor data

def get_auditor_dist(id):
    dist_id = disttovendor.query.filter_by(user_id=id).all()
    vendor_id = [vendor.vendor_id for vendor in dist_id]
    vendor_data = []
    for id in vendor_id:
        temp = {}
        vendor= distvendor.query.filter_by(id=id).first()
        temp["name"] = vendor.vendor_name
        temp["id"] = vendor.id
        temp["latitude"] = vendor.latitude
        temp["longnitude"] = vendor.longnitude
        vendor_data.append(temp)
    return vendor_data


@blueprint.route('/app_login', methods=['GET', 'POST'])
def app_login():
    data = request.get_json(force=True)
    user_name, user_password = data["user_name"], data["user_password"]
    user = userinfo.query.filter_by(name=user_name).first()
    auditor_data = {}
    # user_password = bytes(user_password, encoding='utf8')
    if user and verify_pass(user_password, user.password):
        assigned_role_id = usertorole.query.filter_by(user_id=user.id).first()
        if assigned_role_id:
            role_name = role.query.filter_by(id=assigned_role_id.role_id).first()
        if role_name.name == "auditor":
            auditor_dist = get_auditor_dist(user.id)
            auditor_data = {
                "distributors" : auditor_dist
            }
        return jsonify(status=200,message="user authenticated successfully", user_id=user.id,user_role=role_name.name,auditor_data=auditor_data)
    return jsonify(status=500,message="user authenticated unsuccessfully")
    

@blueprint.route('/get_sku', methods=['GET', 'POST'])
def get_sku():
    sku_data = sku.query.all()
    if sku_data is not None:
        sku_data = [dict(id=sku.id,name=sku.name,
                    description=sku.description,weight=sku.weight) for sku in sku_data]
        return jsonify(status=200,message="sku data delievered",sku_data=sku_data)
    return jsonify(status=500,message="sku data undelievered")
    