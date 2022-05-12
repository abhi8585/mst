# -*- encoding: utf-8 -*-
"""
Copyright (c) 2021
"""
from crypt import methods
from datetime import date, datetime
from email import message
from app.master import blueprint
from app.models import destructionvendor, role, transportvendor, userinfo, usertorole, auditvendor, auditortovendor, distvendor, disttovendor, sku, transportvendor, transtovendor
from app.models import disttobag, audit
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
from app.models import depovendor, depotomaster, depotopicker, depoinventory, pickup, destructiontomaster, destructioninventory
from sqlalchemy import and_


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
    user_data = []
    for user in users:
        temp = {}
        user_role_id = usertorole.query.filter_by(user_id=user.id).first()
        user_role_name = role.query.filter_by(id=user_role_id.role_id).first()
        temp['id'] = user.id
        temp['name'] = user.name
        temp['email'] = user.email
        temp['role_name'] = user_role_name.name
        user_data.append(temp)
    return render_template('list-user-form.html', users=user_data)

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
    user_password = 'eknath'
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
    return json.dumps(dict(message='User added successfully!!'))

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
    vendor_region  = request.form['vendor_region']
    user_exist = auditvendor.query.filter_by(email=vendor_email_id).first()
    if user_exist is not None:
        return jsonify(status=500,message="vendor exist")
    new_aduit_vendor = auditvendor(vendor_code=vendor_code,vendor_name=vendor_name,address=vendor_address,city=vendor_city,
                                    pin_code=vendor_pin_code,state=vendor_state,latitude=vendor_latitude,longnitude=vendor_longnitude,
                                    contact_number=vendor_contact_number, contact_person=vendor_contact_person,email=vendor_email_id,
                                    created_at=datetime.datetime.now(),region_name=vendor_region.lower())
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
    # raise ValueError([vendor.vendor_name for vendor in vendors])
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
    vendor_region  = request.form['vendor_region']
    user_exist = distvendor.query.filter_by(email=vendor_email_id).first()
    if user_exist is not None:
        return jsonify(status=500,message="vendor exist")
    new_dist_vendor = distvendor(vendor_code=vendor_code,vendor_name=vendor_name,address=vendor_address,city=vendor_city,
                                    pin_code=vendor_pin_code,state=vendor_state,latitude=vendor_latitude,longnitude=vendor_longnitude,
                                    contact_number=vendor_contact_number, contact_person=vendor_contact_person,email=vendor_email_id,
                                    created_at=datetime.datetime.now(),region_name=vendor_region)
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
    return jsonify(status=500, message="SKU already inserted!")
    

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
    vendor_region  = request.form['vendor_region']
    user_exist = distvendor.query.filter_by(email=vendor_email_id).first()
    if user_exist is not None:
        return jsonify(status=500,message="vendor exist")
    new_dist_vendor = transportvendor(vendor_code=vendor_code,vendor_name=vendor_name,address=vendor_address,city=vendor_city,
                                    pin_code=vendor_pin_code,state=vendor_state,latitude=vendor_latitude,longnitude=vendor_longnitude,
                                    contact_number=vendor_contact_number, contact_person=vendor_contact_person,email=vendor_email_id,
                                    created_at=datetime.datetime.now(),region_name=vendor_region)
    db.session.add(new_dist_vendor)
    db.session.commit()
    return jsonify(status=200,message="Transporter registered successfully!")



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
    return jsonify(status=200, message="Transporter mapped successfully")



# destruction centre

@blueprint.route('/list/destruction')
def listdestruction():
    vendors = destructionvendor.query.all()
    return render_template("list-destruction-centre-form.html",vendors=vendors)

@blueprint.route('/create/destruction')
def createdestruction():
    return render_template("create-destruction-vendor-form.html")


@blueprint.route("/insert/destruction",methods=['GET', 'POST'])
def insertdestruction():
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
    vendor_region  = request.form['vendor_region']
    user_exist = destructionvendor.query.filter_by(email=vendor_email_id).first()
    if user_exist is not None:
        return jsonify(status=500,message="Destruction centre exist")
    new_dist_vendor = destructionvendor(vendor_code=vendor_code,vendor_name=vendor_name,address=vendor_address,city=vendor_city,
                                    pin_code=vendor_pin_code,state=vendor_state,latitude=vendor_latitude,longnitude=vendor_longnitude,
                                    contact_number=vendor_contact_number, contact_person=vendor_contact_person,email=vendor_email_id,
                                    created_at=datetime.datetime.now(), region_name=vendor_region)
    db.session.add(new_dist_vendor)
    db.session.commit()
    return jsonify(status=200,message="Destuction Centre registered successfully!")



@blueprint.route('/list/destmaster')
def listdestmaster():
    depo_masters = destructiontomaster.query.all()
    auditor_data = []
    for master in depo_masters:
        temp = {}
        vendor_obj = destructionvendor.query.filter_by(id=master.vendor_id).first()
        temp["vendor_name"] = vendor_obj.vendor_name
        user_obj = userinfo.query.filter_by(id=master.user_id).first()
        temp["user_name"] = user_obj.name
        auditor_data.append(temp)
    return render_template("list-dest-form.html",auditor_data=auditor_data)



@blueprint.route('/create/destmaster')
def createdestmaster():
    vendors = destructionvendor.query.all()
    role_obj = role.query.filter_by(name="destruction master").first()
    user_role_obj = usertorole.query.filter_by(role_id=role_obj.id).all()
    user_names = []
    for user in user_role_obj:
        temp = {}
        user_obj = userinfo.query.filter_by(id=user.user_id).first()
        temp["name"] = user_obj.name
        temp["id"] = user_obj.id
        user_names.append(temp)

    return render_template("create-dest-master-form.html",vendors=vendors,user_names=user_names)


@blueprint.route('/map/mapdestmaster',methods=["POST"])
def mapdestmaster():
    user_name = request.form['user_name']
    vendor_name = request.form['vendor_name']
    
    # user_id = userinfo.query.filter_by(name=user_name).first()
    # vendor_id = transportvendor.query.filter_by(id=vendor_name).first()
    dist_vendor_id = destructiontomaster(user_id=user_name, vendor_id=vendor_name, created_at=datetime.now())
    db.session.add(dist_vendor_id)
    db.session.commit()
    return jsonify(status=200, message="Centre Master mapped successfully!")
# depo vendor


@blueprint.route('/list/depovendor')
def listdepovendor():
    vendors = depovendor.query.all()
    return render_template("list-depo-vendor-form.html",vendors=vendors)

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
    vendor_region  = request.form['vendor_region']
    user_exist = depovendor.query.filter_by(email=vendor_email_id).first()
    if user_exist is not None:
        return jsonify(status=500,message="Warehouse exist")
    new_dist_vendor = depovendor(vendor_code=vendor_code,vendor_name=vendor_name,address=vendor_address,city=vendor_city,
                                    pin_code=vendor_pin_code,state=vendor_state,latitude=vendor_latitude,longnitude=vendor_longnitude,
                                    contact_number=vendor_contact_number, contact_person=vendor_contact_person,email=vendor_email_id,
                                    created_at=datetime.datetime.now(),region_name=vendor_region)
    db.session.add(new_dist_vendor)
    db.session.commit()
    return jsonify(status=200,message="Warehouse registered successfully!")

    
@blueprint.route('/create/depomaster')
def createdepomaster():
    vendors = depovendor.query.all()
    role_obj = role.query.filter_by(name="depo master").first()
    user_role_obj = usertorole.query.filter_by(role_id=role_obj.id).all()
    user_names = []
    for user in user_role_obj:
        temp = {}
        user_obj = userinfo.query.filter_by(id=user.user_id).first()
        temp["name"] = user_obj.name
        temp["id"] = user_obj.id
        user_names.append(temp)

    return render_template("create-depo-master-form.html",vendors=vendors,user_names=user_names)

@blueprint.route('/list/depomaster')
def listdepomaster():
    depo_masters = depotomaster.query.all()
    auditor_data = []
    for master in depo_masters:
        temp = {}
        vendor_obj = depovendor.query.filter_by(id=master.vendor_id).first()
        temp["vendor_name"] = vendor_obj.vendor_name
        user_obj = userinfo.query.filter_by(id=master.user_id).first()
        temp["user_name"] = user_obj.name
        auditor_data.append(temp)
    return render_template("list-depo-master-form.html",auditor_data=auditor_data)


@blueprint.route('/map/mapdepomaster',methods=["POST"])
def mapdepomaster():
    user_name = request.form['user_name']
    vendor_name = request.form['vendor_name']
    # user_id = userinfo.query.filter_by(name=user_name).first()
    # vendor_id = transportvendor.query.filter_by(id=vendor_name).first()
    dist_vendor_id = depotomaster(user_id=user_name, vendor_id=vendor_name, created_at=datetime.now())
    db.session.add(dist_vendor_id)
    db.session.commit()
    return jsonify(status=200, message="WareHouse Master mapped successfully!")



# depo picker

@blueprint.route('/create/depopicker')
def createdepopicker():
    vendors = depovendor.query.all()
    role_obj = role.query.filter_by(name="transporter").first()
    user_role_obj = usertorole.query.filter_by(role_id=role_obj.id).all()
    user_names = []
    for user in user_role_obj:
        temp = {}
        user_obj = userinfo.query.filter_by(id=user.user_id).first()
        temp["name"] = user_obj.name
        temp["id"] = user_obj.id
        user_names.append(temp)

    return render_template("create-depo-picker-form.html",vendors=vendors,user_names=user_names)


@blueprint.route('/list/depopicker')
def listdepopicker():
    depo_masters = depotopicker.query.all()
    auditor_data = []
    for master in depo_masters:
        temp = {}
        vendor_obj = depovendor.query.filter_by(id=master.vendor_id).first()
        temp["vendor_name"] = vendor_obj.vendor_name
        user_obj = userinfo.query.filter_by(id=master.user_id).first()
        temp["user_name"] = user_obj.name
        auditor_data.append(temp)
    return render_template("list-depo-picker-form.html",auditor_data=auditor_data)


@blueprint.route('/map/mapdepopicker',methods=["POST"])
def mapdepopicker():
    user_name = request.form['user_name']
    vendor_name = request.form['vendor_name']
    user_id = userinfo.query.filter_by(name=user_name).first()
    vendor_id = depovendor.query.filter_by(id=vendor_name).first()
    dist_vendor_id = depotopicker(user_id=user_name, vendor_id=vendor_name, created_at=datetime.now())
    db.session.add(dist_vendor_id)
    db.session.commit()
    return jsonify(status=200, message="Transporter mapped successfully")




labels = [
    'Audited', 'Picked', 'Collected', 'Dispathched', 'Received',
   
]

# labels = [
#     'JAN', 'FEB', 'MAR', 'APR',
#     'MAY', 'JUN', 'JUL', 'AUG',
#     'SEP', 'OCT', 'NOV', 'DEC'
# ]

values = [
    800, 400, 200, 100, 50
]

colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

# sku analysis
@blueprint.route('/skuanalysis')
def skuanalysis():
    bar_labels=labels
    bar_values=values
    return render_template('sku-analysis.html', title='Bitcoin Monthly Price in USD', max=17000, labels=bar_labels, values=bar_values, set=zip(values, labels, colors))



# helper function for regional distributor data

@blueprint.route('/get_dist_data', methods=["POST"])
def get_dist_data():
    region_name = request.form['region_name']
    dist_data = distvendor.query.filter_by(region_name=region_name.lower()).all()
    dist_table_data = []
    for dist in dist_data:
        temp = {}
        temp['name'] = dist.vendor_name
        audit_count = audit.query.filter_by(dist_id=dist.id).count()
        temp['total_audits'] = audit_count
        temp["audited_bags"] = db.session.query(disttobag).filter(and_(disttobag.dist_id==dist.id, disttobag.status=="audited")).count()
        temp["picked_bags"] = db.session.query(disttobag).filter(and_(disttobag.dist_id==dist.id, disttobag.status=="picked")).count()
        dist_table_data.append(temp)
    return jsonify(dict(data=dist_table_data))

# helper function for regional depo data

@blueprint.route('/get_depo_data', methods=["POST"])
def get_depo_data():
    region_name = request.form['region_name']
    depo_data = depovendor.query.filter_by(region_name=region_name.lower()).all()
    depo_table_data = []
    for depo in depo_data:
        temp = {}
        temp['name'] = depo.vendor_name
        temp["collected_bags"] = db.session.query(depoinventory).filter(and_(depoinventory.status=="collected",depoinventory.depo_id==depo.id)).count()
        temp["dispatched_bags"] = db.session.query(depoinventory).filter(and_(depoinventory.status=="dispatched",depoinventory.depo_id==depo.id)).count()
        depo_table_data.append(temp)
    return jsonify(dict(data=depo_table_data))

# helper function for regional pickup data

@blueprint.route('/get_pickup_data', methods=["POST"])
def get_pickup_data():
    region_name = request.form['region_name']
    dist_data = distvendor.query.filter_by(region_name=region_name.lower()).all()
    pickup_table_data = []
    for dist in dist_data:
        temp = {}
        temp["name"] = dist.vendor_name
        temp["total_pickup"] = pickup.query.filter_by(dist_id=dist.id).count()
        temp["picked_bags"] = db.session.query(disttobag).filter(and_(disttobag.dist_id==dist.id, disttobag.status=="picked")).count()
        pickup_table_data.append(temp)
    return jsonify(dict(data=pickup_table_data))


# helper function for regional destruction data

@blueprint.route('/get_dest_data', methods=["POST"])
def get_dest_data():
    region_name = request.form['region_name']
    dest_data = destructionvendor.query.filter_by(region_name=region_name).all()
    dest_table_data = []
    for dest in dest_data:
        temp = {}
        temp['name'] = dest.vendor_name
        temp["collected_bags"] = db.session.query(destructioninventory).filter(and_(destructioninventory.status=="received",destructioninventory.destruction_id==dest.id)).count()
        dest_table_data.append(temp)
    return jsonify(dict(data=dest_table_data))


    