from email import message

# from sympy import residue
from app import transporter
from app.depo import blueprint
from flask_restful import Resource, Api
from flask import jsonify, render_template, redirect, request, url_for
import json
from app.base.util import verify_pass
from app.models import audit, bag, sku, auditsku, bagtosku, audittobag, disttobag, pickup, picktobag
from app import db
import datetime



# return sku data for a bag with id

def get_sku_data(bag_id):
    sku_data = bagtosku.query.filter_by(bag_id=bag_id).all()
    temp_data = []
    for results in sku_data:
        audit_sku = auditsku.query.filter_by(id=results.sku_id).first()
        sku_obj = sku.query.filter_by(id=audit_sku.sku_id).first()
        if sku_obj is not None:
            temp = {}
            temp["sku_id"] = sku_obj.id
            temp["sku_audit_id"] = audit_sku.id
            temp["sku_weight"]  = audit_sku.weight
            temp["sku_name"] = sku_obj.name
            temp["description"] = sku_obj.description
            temp_data.append(temp)
    return temp_data

@blueprint.route('/get_pickup_order',methods=['GET','POST'])
def get_pickup_order():
    data = request.get_json(force=True)
    pickup_number = data["pickup_number"]
    temp_data = []
    pickup_obj = pickup.query.filter_by(pickup_number=pickup_number).first()
    if pickup_obj is not None:
        bags_data = picktobag.query.filter_by(pick_id=pickup_obj.id).all()
        for results in bags_data:
            temp = {}
            bag_data = bag.query.filter_by(id=results.bag_id).first()
            sku_data = get_sku_data(bag_data.id)
            temp["bag_id"] = bag_data.id
            temp["bag_weight"] = bag_data.weight
            temp["bag_status"] = bag_data.status
            temp["bag_uid"] = bag_data.uid
            temp["bag_sku_data"] = sku_data
            temp_data.append(temp)
    return jsonify(temp_data)
            
            
            