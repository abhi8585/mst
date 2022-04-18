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

from app.models import depotomaster, destructionvendor, transtovendor, transportvendor, depovendor, destructiontomaster, destructionvendor

from app.models import auditortovendor, auditvendor, role, usertorole, userinfo, disttovendor, distvendor, sku, bag
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
        temp["distributor_code"] = vendor.vendor_code
        vendor_data.append(temp)
    return vendor_data

@blueprint.route('/get_distributor', methods=['POST'])
def get_distributor():
    data = request.get_json(force=True)
    user_id = data["user_id"]
    auditor_data = get_auditor_dist(user_id)
    if auditor_data:
        temp = {
            "distributors" : auditor_data
        }
        return jsonify(status=200,distributors=auditor_data)
    return jsonify(status=500,distributors=[])


def get_auditor_vendor(user_id):
    audit_vendor = auditortovendor.query.filter_by(user_id=user_id).first()
    if audit_vendor is not None:
        temp_vendor_name = auditvendor.query.filter_by(id=audit_vendor.auditor_id).first()
        vendor_name = temp_vendor_name.vendor_name
        user_message = "Auditor at {0}".format(vendor_name)
        return dict(status=200,message="vendor found",vendor_name=vendor_name,user_message=user_message)
    else:
        user_message=""
        return dict(status=500,message="no vendor found",vendor_name="",user_message=user_message)


def get_transporter_vendor(user_id):
    transport_vendor = transtovendor.query.filter_by(user_id=user_id).first()
    if transport_vendor is not None:
        vendor_name = transportvendor.query.filter_by(id=transport_vendor.vendor_id).first()
        vendor_name = vendor_name.vendor_name
        user_message = "Transporter at {0}".format(vendor_name)
        return dict(status=200,message="vendor found",vendor_name=vendor_name,user_message=user_message)
    else:
        user_message = ''
        return dict(status=500,message="no vendor found",vendor_name="",user_message=user_message)


def get_depo_vendor(user_id):
    depo_vendor = depotomaster.query.filter_by(user_id=user_id).first()
    if depo_vendor is not None:
        vendor_name = depovendor.query.filter_by(id=depo_vendor.vendor_id).first()
        vendor_name = vendor_name.vendor_name
        user_message = "Depot Master at {0}".format(vendor_name)
        return dict(status=200,message="vendor found",vendor_name=vendor_name, user_message=user_message)
    else:
        user_message = ""
        return dict(status=500,message="no vendor found",vendor_name="", user_message=user_message)


def get_destruction_vendor(user_id):
    destruction_vendor = destructiontomaster.query.filter_by(user_id=user_id).first()
    if destruction_vendor is not None:
        vendor_name = destructionvendor.query.filter_by(id=destruction_vendor.vendor_id).first()
        vendor_name = vendor_name.vendor_name
        user_message = "Destruction Master at {0}".format(vendor_name)
        return dict(status=200,message="vendor found",vendor_name=vendor_name, user_message=user_message)
    else:
        user_message = ""
        return dict(status=500,message="no vendor found",vendor_name="", user_message=user_message)


@blueprint.route('/app_login', methods=['GET', 'POST'])
def app_login():
    data = request.get_json(force=True)
    user_name, user_password = data["user_name"], data["user_password"]
    user_name = user_name.strip()
    # raise ValueError(user_name)
    user = userinfo.query.filter_by(name=user_name).first()
    vendor_name = ""
    auditor_data = {}
    # user_password = bytes(user_password, encoding='utf8')
    if user and verify_pass(user_password, user.password):
        assigned_role_id = usertorole.query.filter_by(user_id=user.id).first()
        if assigned_role_id:
            role_name = role.query.filter_by(id=assigned_role_id.role_id).first()
        if role_name.name == "auditor":
            temp_vendor_name = get_auditor_vendor(user.id)
            vendor_name = temp_vendor_name["vendor_name"]
            user_message = temp_vendor_name["user_message"]
        if role_name.name == "transporter":
            temp_vendor_name = get_transporter_vendor(user.id)
            vendor_name = temp_vendor_name["vendor_name"]
            user_message = temp_vendor_name["user_message"]
        if role_name.name == "depo master":
            temp_vendor_name = get_depo_vendor(user.id)
            vendor_name = temp_vendor_name["vendor_name"]
            user_message = temp_vendor_name["user_message"]
        if role_name.name == "depo picker":
            temp_vendor_name = get_transporter_vendor(user.id)
            vendor_name = temp_vendor_name["vendor_name"]
            user_message = temp_vendor_name["user_message"]
        if role_name.name == "destruction master":
            temp_vendor_name = get_destruction_vendor(user.id)
            vendor_name = temp_vendor_name["vendor_name"]
            user_message = temp_vendor_name["user_message"]
        return jsonify(status=200,message="user authenticated successfully", user_id=user.id,
                        user_role=role_name.name,vendor_name=vendor_name,user_name=user.name.capitalize(),
                        user_message=user_message)
    return jsonify(status=500,message="user authenticated unsuccessfully")
    

@blueprint.route('/get_sku', methods=['GET', 'POST'])
def get_sku():
    sku_data = sku.query.all()
    if sku_data is not None:
        sku_data = [dict(id=sku.id,name=sku.name,
                    description=sku.description,weight=sku.weight) for sku in sku_data
                    if sku.id > 8]
        return jsonify(status=200,message="sku data delievered",sku_data=sku_data)
    return jsonify(status=500,message="sku data undelievered")
    

@blueprint.route('/check_bag_unique', methods=['GET', 'POST'])
def check_bag_unique():
    data = request.get_json(force=True)
    bag_uid = data["bag_uid"]
    try:
        bag_data = bag.query.filter_by(uid=bag_uid).first()
        if bag_data is not None:
            return jsonify(status=200,message="true")
        else:
            return jsonify(status=200,message="false")
    except Exception as e:
        return jsonify(status=500,message="something went wrong")