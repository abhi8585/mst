# -*- encoding: utf-8 -*-
"""
Copyright (c) 2021
"""
from datetime import date, datetime
from email import message
from app.master import blueprint
from app.models import role, transportvendor, userinfo, usertorole, auditvendor, auditortovendor, distvendor, disttovendor, sku, transportvendor, transtovendor
from .. import db
from decouple import config
import json, requests
from flask import jsonify, render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response
# import pdfkit
import os
from app.base.util import hash_pass
from app.base.models import User
# from flask_restful import Resource, Api
from app.models import depovendor, depotomaster


@blueprint.route('/create/role')
def createrole():
    # packages = package.query.all()
    return render_template('create-role-form.html')

@blueprint.route("/insert/role",methods=['GET', 'POST'])
def insertRole():
    role_name = request.form['role_name']
    if role_name == None or role_name=='':
        return json.dumps(dict(status=400,message='role name is not defined')), 400 

    new_role = role(name=role_name,description='abhishek')
    db.session.add(new_role)
    db.session.commit()
    enq=role.query.all()
    # return render_template('enquiry_list.html',enquiry=enq)
    return json.dumps(dict(status=200,message='role created successfully!')), 200


@blueprint.route('/list/role')
def listrole():
    roles=role.query.all()
    # raise ValueError(enq)
    return render_template('list-role-form.html',roles=roles)


# user starting



@blueprint.route('/list/user')
def listuser():
    users = userinfo.query.all()
    return render_template('list-user-form.html', users=users)

#used to insert the user
@blueprint.route("/insert/user",methods=['GET', 'POST'])
def insertuser():
    import string    
    import random
    user_name = request.form['user_name']
    user_email = request.form['user_email']
    # user_password = request.form['user_password']
    user_role_name = request.form['user_role_name']
    # user_password = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))
    user_password = 'abhishek'
    print(user_password)
    user_password_bytes  = hash_pass(user_password)
    new_user_login = User(username=user_name,email=user_email,password=user_password)
    db.session.add(new_user_login)
    db.session.commit()
    new_user=userinfo(name=user_name,password=user_password_bytes,email=user_email)
    db.session.add(new_user)
    db.session.commit()
    new_user_id = new_user.id
    get_role_id = role.query.filter_by(name=user_role_name).first().id
    user_role_mapping = usertorole(user_id=new_user_id, role_id=get_role_id)
    db.session.add(user_role_mapping)
    db.session.commit()
    return json.dumps(dict(user_id='User added successfully!!'))

@blueprint.route('/create/user')
def createuser():
    # packages = package.query.all()
    roles = role.query.all()
    return render_template('create-user-form.html',roles=roles)


# audit vendor

@blueprint.route('/list/auditvendor')
def listauditvendor():
    vendors = auditvendor.query.all()
    return render_template("list-audit-vendor-form.html", vendors=vendors)


@blueprint.route("/insert/auditvendor",methods=['GET', 'POST'])
def insertauditvendor():
    import datetime
    vendor_code = request.form['vendor_code']
    vendor_name = request.form['vendor_name']
    vendor_address = request.form['vendor_address']
    vendor_city = request.form['vendor_city']
    vendor_state = request.form['vendor_state']
    vendor_pin_code = request.form['vendor_pin_code']
    vendor_latitude = request.form['vendor_latitude']
    vendor_longnitude = request.form['vendor_longnitude']
    vendor_contact_number = request.form['vendor_contract_number']
    vendor_contact_person = request.form['vendor_contract_person']
    vendor_email_id =  request.form['vendor_email_id']
    vendor_remark = request.form['vendor_remark']
    user_exist = auditvendor.query.filter_by(email=vendor_email_id).first()
    if user_exist is not None:
        return jsonify(status=500,message="vendor exist")
    new_aduit_vendor = auditvendor(vendor_code=vendor_code,vendor_name=vendor_name,address=vendor_address,city=vendor_city,
                                    pin_code=vendor_pin_code,state=vendor_state,latitude=vendor_latitude,longnitude=vendor_longnitude,
                                    contact_number=vendor_contact_number, contact_person=vendor_contact_person,email=vendor_email_id,
                                    created_at=datetime.datetime.now())
    db.session.add(new_aduit_vendor)
    db.session.commit()
    return jsonify(status=200,message="Vendor registered successfully!")
    

@blueprint.route('/create/auditvendor')
def createauditvendor():
    # packages = package.query.all()
    roles = role.query.all()
    return render_template('create-audit-vendor-form.html',roles=roles)


# auditor

@blueprint.route('/list/auditor')
def listauditor():
    auditor_users = auditortovendor.query.all()
    auditor_data = []
    for user in auditor_users:
        temp = {}
        user_name = userinfo.query.filter_by(id=user.user_id).first()
        temp["user_name"] = user_name.name
        vendor_name = auditvendor.query.filter_by(id=user.auditor_id).first()
        temp["vendor_name"] = vendor_name.vendor_name
        auditor_data.append(temp)

    return render_template("list-auditor-form.html",auditor_data=auditor_data)


@blueprint.route('create/auditor')
def createauditor():
    vendors = auditvendor.query.all()
    auditor_role_id = role.query.filter_by(name="auditor").first()
    auditor_users = usertorole.query.filter_by(role_id=auditor_role_id.id).all()
    user_ids = [user.user_id for user in auditor_users]
    user_names = []
    for id in user_ids:
        user_name = userinfo.query.filter_by(id=id).first()
        if user_name is not None:
            user_names.append(user_name.name)
    return render_template("create-auditor-form.html",vendors=vendors, user_names=user_names)

@blueprint.route('map/auditor',methods=['GET', 'POST'])
def mapauditor():
    user_name = request.form['user_name']
    vendor_name = request.form['vendor_name']
    user_id = userinfo.query.filter_by(name=user_name).first()
    vendor_id = auditvendor.query.filter_by(vendor_name=vendor_name).first()
    auditor_exist = auditortovendor.query.filter_by(user_id=user_id.id).first()
    if auditor_exist is not None:
        return jsonify(status=500, message="Auditor already mapped!")
    auditor_vendor_id = auditortovendor(user_id=user_id.id, auditor_id=vendor_id.id)
    db.session.add(auditor_vendor_id)
    db.session.commit()
    return jsonify(status=200, message="auditor mapped successfully")


#distributor vendor

@blueprint.route('/list/distvendor')
def listdistvendor():
    vendors = distvendor.query.all()
    return render_template("list-dist-vendor-form.html",vendors=vendors)

@blueprint.route('/create/distvendor')
def createdistvendor():
    # packages = package.query.all()
    roles = role.query.all()
    return render_template('create-dist-vendor-form.html',roles=roles)


@blueprint.route("/insert/distvendor",methods=['GET', 'POST'])
def insertdistvendor():
    import datetime
    vendor_code = request.form['vendor_code']
    vendor_name = request.form['vendor_name']
    vendor_address = request.form['vendor_address']
    vendor_city = request.form['vendor_city']
    vendor_state = request.form['vendor_state']
    vendor_pin_code = request.form['vendor_pin_code']
    vendor_latitude = request.form['vendor_latitude']
    vendor_longnitude = request.form['vendor_longnitude']
    vendor_contact_number = request.form['vendor_contract_number']
    vendor_contact_person = request.form['vendor_contract_person']
    vendor_email_id =  request.form['vendor_email_id']
    vendor_remark = request.form['vendor_remark']
    user_exist = distvendor.query.filter_by(email=vendor_email_id).first()
    if user_exist is not None:
        return jsonify(status=500,message="vendor exist")
    new_dist_vendor = distvendor(vendor_code=vendor_code,vendor_name=vendor_name,address=vendor_address,city=vendor_city,
                                    pin_code=vendor_pin_code,state=vendor_state,latitude=vendor_latitude,longnitude=vendor_longnitude,
                                    contact_number=vendor_contact_number, contact_person=vendor_contact_person,email=vendor_email_id,
                                    created_at=datetime.datetime.now())
    db.session.add(new_dist_vendor)
    db.session.commit()
    return jsonify(status=200,message="Vendor registered successfully!")


# distributor

@blueprint.route('/list/distributor')
def listdistributor():
    auditor_users = disttovendor.query.all()
    auditor_data = []
    for user in auditor_users:
        temp = {}
        role_id = role.query.filter_by(name="auditor").first()
        user_name = userinfo.query.filter_by(id=user.user_id).first()
        user_role_id = usertorole.query.filter_by(user_id=user_name.id).first()
        if user_role_id.role_id == role_id.id:
            temp["user_name"] = user_name.name
            vendor_name = distvendor.query.filter_by(id=user.vendor_id).first()
            temp["vendor_name"] = vendor_name.vendor_name
            auditor_data.append(temp)

    return render_template("list-distributor-form.html",auditor_data=auditor_data)


@blueprint.route('/list/disttransporter')
def listdisttransporter():
    auditor_users = disttovendor.query.all()
    auditor_data = []
    for user in auditor_users:
        temp = {}
        role_id = role.query.filter_by(name="transporter").first()
        user_name = userinfo.query.filter_by(id=user.user_id).first()
        user_role_id = usertorole.query.filter_by(user_id=user_name.id).first()
        if user_role_id.role_id == role_id.id:
            temp["user_name"] = user_name.name
            vendor_name = distvendor.query.filter_by(id=user.vendor_id).first()
            temp["vendor_name"] = vendor_name.vendor_name
            auditor_data.append(temp)

    return render_template("list-distributor-transport-form.html",auditor_data=auditor_data)


@blueprint.route('create/distributor')
def createdistributor():
    vendors = distvendor.query.all()
    auditor_role_id = role.query.filter_by(name="auditor").first()
    auditor_users = usertorole.query.filter_by(role_id=auditor_role_id.id).all()
    user_ids = [user.user_id for user in auditor_users]
    user_names = []
    for id in user_ids:
        user_name = userinfo.query.filter_by(id=id).first()
        if user_name is not None:
            user_names.append(user_name.name)
    return render_template("create-distributor-form.html",vendors=vendors, user_names=user_names)

@blueprint.route('create/transdistributor')
def createtransdistributor():
    vendors = distvendor.query.all()
    auditor_role_id = role.query.filter_by(name="transporter").first()
    auditor_users = usertorole.query.filter_by(role_id=auditor_role_id.id).all()
    user_ids = [user.user_id for user in auditor_users]
    user_names = []
    for id in user_ids:
        user_name = userinfo.query.filter_by(id=id).first()
        if user_name is not None:
            user_names.append(user_name.name)
    return render_template("create-distributor-transport-form.html",vendors=vendors, user_names=user_names)

@blueprint.route('map/distributor',methods=['GET', 'POST'])
def mapdistributor():
    user_name = request.form['user_name']
    vendor_name = request.form['vendor_name']
    user_id = userinfo.query.filter_by(name=user_name).first()
    vendor_id = distvendor.query.filter_by(vendor_name=vendor_name).first()
    dist_vendor_id = disttovendor(user_id=user_id.id, vendor_id=vendor_id.id)
    db.session.add(dist_vendor_id)
    db.session.commit()
    return jsonify(status=200, message="distributor mapped successfully")


# SKU

@blueprint.route('/list/sku')
def listsku():
    sku_data = sku.query.all()
    return render_template("list-sku-form.html",sku_data=sku_data)

@blueprint.route('/create/sku')
def createsku():
    # packages = package.query.all()
    # roles = role.query.all()
    return render_template('create-sku-form.html')

@blueprint.route('/insert/sku',methods=['GET', 'POST'])
def insertsku():
    sku_name = request.form['sku_name']
    sku_description = request.form['sku_description']
    sku_weight = request.form['sku_weight']
    check_sku = sku.query.filter_by(name=sku_name).first()
    if check_sku is None:
        new_sku = sku(name=sku_name, description=sku_description, weight=sku_weight,
                    created_at=datetime.now())
        db.session.add(new_sku)
        db.session.commit()
        return jsonify(status=200, message="sku inserted successfully!")
    return jsonify(status=500, message="sku inserted unsuccessfully!")
    

# transport

# transport vendor

@blueprint.route('/list/transvendor')
def listtransvendor():
    vendors = transportvendor.query.all()
    return render_template("list-trans-vendor-form.html",vendors=vendors)


@blueprint.route('/create/transvendor')
def createtransvendor():
    # vendors = distvendor.query.all()
    return render_template("create-trans-vendor-form.html")


@blueprint.route("/insert/transvendor",methods=['GET', 'POST'])
def inserttransvendor():
    import datetime
    vendor_code = request.form['vendor_code']
    vendor_name = request.form['vendor_name']
    vendor_address = request.form['vendor_address']
    vendor_city = request.form['vendor_city']
    vendor_state = request.form['vendor_state']
    vendor_pin_code = request.form['vendor_pin_code']
    vendor_latitude = request.form['vendor_latitude']
    vendor_longnitude = request.form['vendor_longnitude']
    vendor_contact_number = request.form['vendor_contract_number']
    vendor_contact_person = request.form['vendor_contract_person']
    vendor_email_id =  request.form['vendor_email_id']
    vendor_remark = request.form['vendor_remark']
    user_exist = distvendor.query.filter_by(email=vendor_email_id).first()
    if user_exist is not None:
        return jsonify(status=500,message="vendor exist")
    new_dist_vendor = transportvendor(vendor_code=vendor_code,vendor_name=vendor_name,address=vendor_address,city=vendor_city,
                                    pin_code=vendor_pin_code,state=vendor_state,latitude=vendor_latitude,longnitude=vendor_longnitude,
                                    contact_number=vendor_contact_number, contact_person=vendor_contact_person,email=vendor_email_id,
                                    created_at=datetime.datetime.now())
    db.session.add(new_dist_vendor)
    db.session.commit()
    return jsonify(status=200,message="Vendor registered successfully!")



# transporter

@blueprint.route('/list/transporter')
def listtransporter():
    auditor_users = transtovendor.query.all()
    auditor_data = []
    for user in auditor_users:
        temp = {}
        user_name = userinfo.query.filter_by(id=user.user_id).first()
        temp["user_name"] = user_name.name
        vendor_name = transportvendor.query.filter_by(id=user.vendor_id).first()
        temp["vendor_name"] = vendor_name.vendor_name
        auditor_data.append(temp)
    return render_template("list-trans-form.html",auditor_data=auditor_data)

@blueprint.route('/create/transporter')
def createtransporter():
    vendors = transportvendor.query.all()
    role_id = role.query.filter_by(name="transporter").first()
    trans_users = usertorole.query.filter_by(role_id=role_id.id).all()
    user_names = []
    for user in trans_users:
        user_obj = userinfo.query.filter_by(id=user.id).first()
        user_names.append(user_obj.name)
    return render_template("create-trans-form.html",vendors=vendors,user_names=user_names)


@blueprint.route('/map/transporter',methods=["POST"])
def maptransporter():
    user_name = request.form['user_name']
    vendor_name = request.form['vendor_name']
    user_id = userinfo.query.filter_by(name=user_name).first()
    vendor_id = transportvendor.query.filter_by(id=vendor_name).first()
    dist_vendor_id = transtovendor(user_id=user_id.id, vendor_id=vendor_id.id, created_at=datetime.now())
    db.session.add(dist_vendor_id)
    db.session.commit()
    return jsonify(status=200, message="distributor mapped successfully")


# depo vendor


@blueprint.route('/list/depovendor')
def listdepovendor():
    return render_template("list-depo-vendor-form.html")

@blueprint.route('/create/depovendor')
def createdepovendor():
    return render_template("create-depo-vendor-form.html")

@blueprint.route("/insert/depovendor",methods=['GET', 'POST'])
def insertdepovendor():
    import datetime
    vendor_code = request.form['vendor_code']
    vendor_name = request.form['vendor_name']
    vendor_address = request.form['vendor_address']
    vendor_city = request.form['vendor_city']
    vendor_state = request.form['vendor_state']
    vendor_pin_code = request.form['vendor_pin_code']
    vendor_latitude = request.form['vendor_latitude']
    vendor_longnitude = request.form['vendor_longnitude']
    vendor_contact_number = request.form['vendor_contract_number']
    vendor_contact_person = request.form['vendor_contract_person']
    vendor_email_id =  request.form['vendor_email_id']
    vendor_remark = request.form['vendor_remark']
    user_exist = depovendor.query.filter_by(email=vendor_email_id).first()
    if user_exist is not None:
        return jsonify(status=500,message="vendor exist")
    new_dist_vendor = depovendor(vendor_code=vendor_code,vendor_name=vendor_name,address=vendor_address,city=vendor_city,
                                    pin_code=vendor_pin_code,state=vendor_state,latitude=vendor_latitude,longnitude=vendor_longnitude,
                                    contact_number=vendor_contact_number, contact_person=vendor_contact_person,email=vendor_email_id,
                                    created_at=datetime.datetime.now())
    db.session.add(new_dist_vendor)
    db.session.commit()
    return jsonify(status=200,message="Vendor registered successfully!")
