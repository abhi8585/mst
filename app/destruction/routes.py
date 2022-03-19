from email import message
from app.destruction import blueprint
from flask_restful import Resource, Api
from flask import jsonify, render_template, redirect, request, url_for
import json
from app.base.util import verify_pass
from app.models import destructiontomaster, destructionvendor, depopickup, deviateddepopickbag, depopicktobag
from app import db
import datetime

from app.models import bag, bagtosku, auditsku, sku, destructioninventory, deviateddestructionbag



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


@blueprint.route('/create_destruction', methods=['GET', 'POST'])
def create_destruction():
    des_obj = destructionvendor(vendor_code="des2",vendor_name="des2",address="pratap vihar",city="ghaziabad",pin_code='201009',
                                state="uttar pradesh",latitude='12.12', longnitude='71.12',contact_person = 'abhi',
                                contact_number='8585945196',email='des2@gmail.com', created_at=datetime.datetime.now())
    db.session.add(des_obj)
    db.session.commit()
    return "object created"



@blueprint.route('/map_destruction', methods=['GET', 'POST'])
def map_destruction():
    des_map_obj = destructiontomaster(vendor_id=1, user_id=16, created_at = datetime.datetime.now())
    db.session.add(des_map_obj)
    db.session.commit()
    return "object created"



@blueprint.route('/get_destruction',methods=['GET','POST'])
def get_destruction():
    data = request.get_json(force=True)
    destruction_master_id = data["destruction_master_id"]
    depo_master_data = destructiontomaster.query.filter_by(user_id=destruction_master_id).all()
    depo_data = []
    if len(depo_master_data) != 0:
        for depo_master in depo_master_data:
            temp = {}
            depo_obj = destructionvendor.query.filter_by(id=depo_master.vendor_id).first()
            temp["destruction_centre_id"] = depo_obj.id
            temp["destruction_centre_name"] = depo_obj.vendor_name
            depo_data.append(temp)
        return jsonify(status=200,depo_data=depo_data,message="depo data delieverd!")

    else:

        return jsonify(status=500,message="empty depo data")


@blueprint.route('/get_asn_number_data',methods=['GET','POST'])
def get_asn_number_data():
    data = request.get_json(force=True)
    asn_number = data["asn_number"]
    temp_data = []
    pickup_obj = depopickup.query.filter_by(asn_number=asn_number).first()
    if pickup_obj is not None:
        bags_data = depopicktobag.query.filter_by(pick_id=pickup_obj.id).all()
        for results in bags_data:
            temp = {}
            if results.status == "incorrect":
                bag_dev_obj = deviateddepopickbag.query.filter_by(bag_id = results.bag_id).first()
                temp["bag_weight"] = bag_dev_obj.weight    
                bag_data = bag.query.filter_by(id=results.bag_id).first()
                sku_data = get_sku_data(bag_data.id)
                temp["bag_id"] = bag_data.id
                temp["bag_status"] = results.status
                temp["bag_uid"] = bag_data.uid
                temp["bag_sku_data"] = sku_data
                temp_data.append(temp)
            else:
                bag_data = bag.query.filter_by(id=results.bag_id).first()
                sku_data = get_sku_data(bag_data.id)
                temp["bag_weight"] = bag_data.weight 
                temp["bag_id"] = bag_data.id
                temp["bag_status"] = results.status
                temp["bag_uid"] = bag_data.uid
                temp["bag_sku_data"] = sku_data
                temp_data.append(temp)
        return jsonify(status=200,asn_data=temp_data,message="pickup data delievered!")
    else:
        return jsonify(status=500,asn_data=temp_data,message="no pickup found!")


# get bag data will be as same as from trasnporter


# submit pickup at destruction centre


destruction_object = {

    "asn_number" : "ASN00MND00TNT8",
    "destruction_master_id" : "14",
    "destruction_id" : "1",
    "latitude" : "30.85",
    "longnitude" : "75.85",
    "bag_data" : [
        {
            "bag_id" : "177",
            "bag_weight" : "25",
            "status": "correct",
            "deviated_data" : ""

        },
        {
            "bag_id" : "178",
            "bag_weight" : "25",
            "status": "correct",
            "deviated_data" : ""

        },
        {
            "bag_id" : "179",
            "bag_weight" : "25",
            "status": "correct",
            "deviated_data" : ""

        },
        {
            "bag_id" : "180",
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
    asn_number = data["asn_number"]
    destruction_master_id = data["destruction_master_id"]
    destruction_id = data["destruction_id"]
    latitude = data["latitude"]
    longnitude = data["longnitude"]
    bag_data = data["bag_data"]
    if bag is not None and len(bag_data) !=0:
        for temp_bag in bag_data:
            if temp_bag["status"] == "incorrect":
                submit_obj = destructioninventory(destruction_id=destruction_id,bag_id=temp_bag["bag_id"],status="received",latitude=latitude,
                                            longnitude=longnitude,created_at=datetime.datetime.now(),
                                            submitted_by=destruction_master_id)
                deviated_data = temp_bag["deviated_data"]
                deviated_bag_obj = deviateddestructionbag(bag_id=temp_bag["bag_id"],weight=deviated_data["weight"],
                                               remarks=deviated_data["remarks"], created_at=datetime.datetime.now())
                db.session.add(submit_obj)
                db.session.add(deviated_bag_obj)
                bag_obj = bag.query.filter_by(id=temp_bag["bag_id"]).first()
                bag_obj.status = "received"
                db.session.commit()
            else:
                submit_obj = destructioninventory(destruction_id=destruction_id,bag_id=temp_bag["bag_id"],status="received",latitude=latitude,
                                            longnitude=longnitude,created_at=datetime.datetime.now(),
                                            submitted_by=destruction_master_id)
                db.session.add(submit_obj)
                bag_obj = bag.query.filter_by(id=temp_bag["bag_id"]).first()
                bag_obj.status = "received"
                db.session.commit()
        pickup_obj = depopickup.query.filter_by(asn_number=asn_number).first()
        pickup_obj.status = "collected"
        db.session.commit()
        return jsonify(status=200,message="pickup saved successfully!")
    else:
        return jsonify(status=500,message="no data to save")

