from email import message
from app import transporter
from app.picker import blueprint
from flask_restful import Resource, Api
from flask import jsonify, render_template, redirect, request, url_for
import json
from app.base.util import verify_pass
from app.models import audit, bag, sku, auditsku, bagtosku, audittobag, disttobag, pickup, picktobag, transtovendor, transportvendor, disttovendor, distvendor
from app.models import deviatedbag

from app.models import depotopicker, depovendor, depopickup, depoinventory, depopicktobag, deviateddepopickbag, depoinventory
from app import db
import datetime



def get_picker_depo_data(id):
    dist_id = depotopicker.query.filter_by(user_id=id).all()
    vendor_id = [vendor.vendor_id for vendor in dist_id]
    vendor_data = []
    for id in vendor_id:
        temp = {}
        vendor= depovendor.query.filter_by(id=id).first()
        temp["name"] = vendor.vendor_name
        temp["id"] = vendor.id
        temp["latitude"] = vendor.latitude
        temp["longnitude"] = vendor.longnitude
        vendor_data.append(temp)
    return vendor_data

@blueprint.route('/get_picker_depo',methods=['GET','POST'])
def get_picker_depo():
    data = request.get_json(force=True)
    user_id = data["user_id"]
    picker_data = get_picker_depo_data(user_id)
    if picker_data:
        temp = {
            "depos" : picker_data
        }
        return jsonify(status=200,depos=picker_data)
    return jsonify(status=500,depos=[])



pickup_object = {
    "picker_id" : "15",
    "truck_number" : "12345",
    "latitude" : "23.32",
    "longnitude" : "23.78",
    "depo_id" : "3",
    "bag_data" : [
        {
            "bag_id" : "177",
            "bag_weight" : "25",
            "status": "correct",
            "deviated_data" : "",

        },
        {
            "bag_id" : "178",
            "bag_weight" : "25",
            "status": "correct",
            "deviated_data" : "",

        },
        {
            "bag_id" : "179",
            "bag_weight" : "25",
            "status": "correct",
            "deviated_data" : "",

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
    

# create depo pickup object and map it to bag
@blueprint.route('/create_pickup',methods=["GET","POST"])
def create_pickup():
    import string
    import random
    data = request.get_json(force=True)
    picker_id = data["picker_id"]
    truck_number = data["truck_number"]
    latitude = data["latitude"]
    longnitude = data["longnitude"]
    depo_id = data["depo_id"]
    bag_data = data["bag_data"]
    pickup_number = depopickup.query.count() + 1
    asn_number = "ASN00MND00TNT{0}".format(pickup_number)
    pickup_obj = depopickup(picker_id=picker_id,truck_number=truck_number,latitude=latitude,longnitude=longnitude,
                        depo_id=depo_id,asn_number=asn_number,status="picked",created_at=datetime.datetime.now())
    db.session.add(pickup_obj)
    db.session.commit()
    if len(bag_data) != 0:
        for bag_id in bag_data:
            if bag_id["deviated_data"] != "" and bag_id["status"] == "incorrect":
                temp = bag_id["deviated_data"]
                deviate_bag = deviateddepopickbag(bag_id=bag_id["bag_id"],weight=temp["weight"],
                                        remarks=temp["remarks"],created_at=datetime.datetime.now())
                pick_bag_obj = depopicktobag(bag_id=bag_id["bag_id"],pick_id=pickup_obj.id,
                                    status=bag_id["status"],created_at=datetime.datetime.now())
                db.session.add(pick_bag_obj)
                db.session.add(deviate_bag)
                temp_bag_obj = bag.query.filter_by(id=bag_id["bag_id"]).first()
                temp_bag_obj.status = "dispatched"
                temp_dist_bag = depoinventory.query.filter_by(bag_id=bag_id["bag_id"]).first()
                temp_dist_bag.status = "dispatched"
                db.session.commit()
            else:
                # temp_bag = bag_id
                temp_bag_obj = bag.query.filter_by(id=bag_id["bag_id"]).first()
                if temp_bag_obj.weight == bag_id["bag_weight"]:
                    pick_bag_obj = depopicktobag(bag_id=bag_id["bag_id"],pick_id=pickup_obj.id,
                                    status=bag_id["status"],created_at=datetime.datetime.now())
                    db.session.add(pick_bag_obj)
                    temp_bag_obj.status = "dispatched"
                    temp_dist_bag = depoinventory.query.filter_by(bag_id=bag_id["bag_id"]).first()
                    temp_dist_bag.status = "dispatched"
                    db.session.commit()
        return jsonify(status=200,pickup_number = asn_number,message="depo pickup saved successfully!")
    else:
        return jsonify(status=500,message="no bag data to store!")


@blueprint.route('/get_depo_pickup', methods=['POST'])
def get_depo_pickup():
    data = request.get_json(force=True)
    picker_id = data["picker_id"]
    pickup_obj = depopickup.query.filter_by(picker_id=picker_id, status="picked").all()
    pickup_data = []
    if pickup_obj is not None:
        for pick in pickup_obj:
            temp = {}
            bag_count = depopicktobag.query.filter_by(pick_id=pick.id).count()
            temp["total_bag"] = bag_count
            temp["pickup_number"] = pick.asn_number
            temp["date"] = pick.created_at
            pickup_data.append(temp)
    else:
        return jsonify(status=500,message="no pickups")
    if len(pickup_data) != 0:
        return jsonify(status=200,pickup_data=pickup_data)
    else:
        return jsonify(status=500,message="no pickup")