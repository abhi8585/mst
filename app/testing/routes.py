from email import message
from operator import sub
from re import M
from sys import exec_prefix

from itsdangerous import exc
from app import transporter
from app.testing import blueprint
from flask_restful import Resource, Api
from flask import jsonify, render_template, redirect, request, url_for
import json
from app.base.util import verify_pass
from app.models import audit, bag, depopickup, sku, auditsku, bagtosku, audittobag, disttobag, pickup, picktobag, transtovendor, transportvendor, disttovendor, distvendor, userinfo
from app.models import deviatedbag
from app import db
import datetime

from app import mail

from flask_mail import Message
from tabulate import tabulate



@blueprint.route('/test_audit',methods=['GET','POST'])
def get_dist_order():
    data = request.get_json(force=True)
    bags_data = data["bags"]
    
    testing_logs = []

    for temp_bag in bags_data:
        try:
            bag_obj = bag.query.filter_by(uid=temp_bag["bag_uid"]).first()
            if bag_obj is not None:
                temp = {}
                if bag_obj.weight == temp_bag["bag_weight"]:
                    temp["weight_check"] = "pass"
                if bag_obj.uid == temp_bag["bag_uid"]:
                    temp["uid_check"] = "pass"
                temp_sku_count = bagtosku.query.filter_by(bag_id=bag_obj.id).all()
                if len(temp_sku_count) == len(temp_bag["sku"]):
                    temp["sku_count"] = "pass"
                testing_logs.append(temp)
            else:
                temp = {}
                temp[temp_bag["bag_uid"]] = None
                testing_logs.append(temp)

        except Exception as e:
            print(e)
            temp = {}
            temp[temp_bag["bag_uid"]] = None
            testing_logs.append(temp)
    return jsonify(testing_logs = testing_logs)



# tp create trasnport pickup structure
@blueprint.route('/create_transport_pickup',methods=['GET','POST'])
def create_transport_pickup():
    temp = {
        "transporter_id" : "12",
        "lr_number" : "LRJIMMY001",
        "truck_number" : "up 18 ls 8645",
        "latitude" : "23.32",
        "longnitude" : "23.78",
        "dist_id" : "2",
        "bag_data" : []
    }
    data = request.get_json(force=True)
    bags_data = data["bags"]
    for temp_bag in bags_data:
        bag_sample = {
            "bag_id" : "",
            "bag_weight" : "",
            "status": "",
            "deviated_data" : ""

        }
        bag_obj = bag.query.filter_by(uid=temp_bag["bag_uid"]).first()
        bag_sample["bag_id"] = bag_obj.id
        bag_sample["bag_weight"] = bag_obj.weight
        bag_sample["status"] = "correct"
        temp["bag_data"].append(bag_sample)
    return jsonify(temp)
        

@blueprint.route('/create_depo_submit',methods=['GET','POST'])
def create_depo_submit():
    temp = {
        "depo_master_id": "14",
        "depo_id": "1",
        "truck_number": "",
        "latitude": 28.5846026,
        "longnitude": 77.3810236,
        "bag_data": [],
    }
    data = request.get_json(force=True)
    bags_data = data["bags"]
    for temp_bag in bags_data:
        bag_sample = {
            "bag_id" : "",
            "bag_weight" : "",
            "status": "",
            "deviated_data" : ""

        }
        bag_obj = bag.query.filter_by(uid=temp_bag["bag_uid"]).first()
        bag_sample["bag_id"] = bag_obj.id
        bag_sample["bag_weight"] = bag_obj.weight
        bag_sample["status"] = "correct"
        temp["bag_data"].append(bag_sample)
    return jsonify(temp)
        

@blueprint.route('/create_picker_pickup',methods=['GET','POST'])
def create_picker_pickup():
    temp = {
        "picker_id" : "15",
        "truck_number" : "up 14 aj 4090",
        "lr_number" : "lrans0100221",
        "latitude" : "23.32",
        "longnitude" : "23.78",
        "depo_id" : "3",
        "bag_data" : []
    }
    data = request.get_json(force=True)
    bags_data = data["bags"]
    for temp_bag in bags_data:
        bag_sample = {
            "bag_id" : "",
            "bag_weight" : "",
            "status": "",
            "deviated_data" : ""

        }
        bag_obj = bag.query.filter_by(uid=temp_bag["bag_uid"]).first()
        bag_sample["bag_id"] = bag_obj.id
        bag_sample["bag_weight"] = bag_obj.weight
        bag_sample["status"] = "correct"
        temp["bag_data"].append(bag_sample)
    return jsonify(temp)
        
# create destruction strucutre

@blueprint.route('/create_destruction_lr_submit',methods=['GET','POST'])
def create_destruction_lr_submit():
    temp = {
        "lr_number" : "lrjimmy001",
        "destruction_master_id" : "14",
        "deviated_weight" : "100.00",
        "destruction_id" : "1",
        "latitude" : "30.85",
        "longnitude" : "75.85",
        "bag_data" : []

    }
    data = request.get_json(force=True)
    bags_data = data["bags"]
    for temp_bag in bags_data:
        bag_sample = {
            "bag_id" : "",
            "bag_weight" : "",
            "status": "",
            "deviated_data" : ""

        }
        bag_obj = bag.query.filter_by(uid=temp_bag["bag_uid"]).first()
        bag_sample["bag_id"] = bag_obj.id
        bag_sample["bag_weight"] = bag_obj.weight
        bag_sample["status"] = "correct"
        temp["bag_data"].append(bag_sample)
    return jsonify(temp)
        
