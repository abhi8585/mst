from email import message

# from sympy import residue
from app import transporter
from app.depo import blueprint
from flask_restful import Resource, Api
from flask import jsonify, render_template, redirect, request, url_for
import json
from app.base.util import verify_pass
from app.models import audit, bag, depotomaster, depovendor, sku, auditsku, bagtosku, audittobag, disttobag, pickup, picktobag, deviatedbag
from app import db
from app.models import depoinventory, deviateddepobag
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
            if results.status == "incorrect":
                bag_dev_obj = deviatedbag.query.filter_by(bag_id = results.bag_id).first()
                temp["bag_weight"] = bag_dev_obj.weight    
                bag_data = bag.query.filter_by(id=results.bag_id).first()
                sku_data = get_sku_data(bag_data.id)
                temp["bag_id"] = bag_data.id
                temp["bag_status"] = results.status
                temp["bag_uid"] = bag_data.uid
                temp["bag_sku_data"] = sku_data
                temp_data.append(temp)
            else:
                # bag_dev_obj = deviatedbag.query.filter_by(bag_id = results.bag_id).first()
                       
                    bag_data = bag.query.filter_by(id=results.bag_id).first()
                    sku_data = get_sku_data(bag_data.id)
                    temp["bag_weight"] = bag_data.weight 
                    temp["bag_id"] = bag_data.id
                    temp["bag_status"] = results.status
                    temp["bag_uid"] = bag_data.uid
                    temp["bag_sku_data"] = sku_data
                    temp_data.append(temp)
    return jsonify(pickup_data=temp_data)


depo_object = {

    "pickup_number" : "6",
    "depo_master_id" : "14",
    "depo_id" : "1",
    "latitude" : "30.85",
    "longnitude" : "75.85",
    "bag_data" : [
        {
            "bag_id" : "1",
            "bag_weight" : "25",
            "status": "correct",
            "deviated_data" : ""

        },
        {
            "bag_id" : "2",
            "bag_weight" : "25",
            "status": "correct",
            "deviated_data" : ""

        },
        {
            "bag_id" : "3",
            "bag_weight" : "25",
            "status": "correct",
            "deviated_data" : ""

        },
        {
            "bag_id" : "4",
            "bag_weight" : "25",
            "status": "incorrect",
            "deviated_data" : {
                "weight" : "15",
                "remarks" : "weight is less"
            }

        }
    
    ]
    

}
            
            
@blueprint.route('/submit_pickup',methods=['GET','POST'])
def submit_pickup():
    data = request.get_json(force=True)
    pickup_number = data["pickup_number"]
    depo_master_id = data["depo_master_id"]
    depo_id = data["depo_id"]
    latitude = data["latitude"]
    longnitude = data["longnitude"]
    bag_data = data["bag_data"]
    if bag is not None and len(bag_data) !=0:
        for temp_bag in bag_data:
            if temp_bag["status"] == "incorrect":
                submit_obj = depoinventory(depo_id=depo_id,bag_id=temp_bag["bag_id"],status="collected",latitude=latitude,
                                            longnitude=longnitude,created_at=datetime.datetime.now(),
                                            submitted_by=depo_master_id)
                deviated_data = temp_bag["deviated_data"]
                deviated_bag_obj = deviateddepobag(bag_id=temp_bag["bag_id"],weight=deviated_data["weight"],
                                               remarks=deviated_data["remarks"], created_at=datetime.datetime.now())
                db.session.add(submit_obj)
                db.session.add(deviated_bag_obj)
                bag_obj = bag.query.filter_by(id=temp_bag["bag_id"]).first()
                bag_obj.status = "collected"
                db.session.commit()
            else:
                submit_obj = depoinventory(depo_id=depo_id,bag_id=temp_bag["bag_id"],status="collected",latitude=latitude,
                                            longnitude=longnitude,created_at=datetime.datetime.now(),
                                            submitted_by=depo_master_id)
                db.session.add(submit_obj)
                bag_obj = bag.query.filter_by(id=temp_bag["bag_id"]).first()
                bag_obj.status = "collected"
                db.session.commit()
        pickup_obj = pickup.query.filter_by(pickup_number=pickup_number).first()
        pickup_obj.status = "collected"
        db.session.commit()
        return jsonify(status=200,message="pickup saved successfully!")
    else:
        return jsonify(status=500,message="no data to save")


@blueprint.route('/get_depo',methods=['GET','POST'])
def get_depo():
    data = request.get_json(force=True)
    depo_master_id = data["depo_master_id"]
    depo_master_data = depotomaster.query.filter_by(user_id=depo_master_id).all()
    depo_data = []
    if len(depo_master_data) != 0:
        for depo_master in depo_master_data:
            temp = {}
            depo_obj = depovendor.query.filter_by(id=depo_master.vendor_id).first()
            temp["depo_id"] = depo_obj.id
            temp["depo_name"] = depo_obj.vendor_name
            depo_data.append(temp)
        return jsonify(status=200,depo_data=depo_data,message="depo data delieverd!")

    else:

        return jsonify(status=500,message="empty depo data")