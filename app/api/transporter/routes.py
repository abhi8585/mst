from email import message
from app import transporter
from app.transporter import blueprint
from flask_restful import Resource, Api
from flask import jsonify, render_template, redirect, request, url_for
import json
from app.base.util import verify_pass
from app.models import audit, bag, sku, auditsku, bagtosku, audittobag, disttobag, pickup, picktobag
from app import db
import datetime



# @blueprint.route('/get_dist_order',methods=['GET','POST'])
# def get_dist_order():
#     data = request.get_json(force=True)
#     dist_id = data["dist_id"]
#     data = db.session.query(disttobag.bag_id,bagtosku.sku_id).outerjoin(disttobag, bagtosku.bag_id == disttobag.bag_id).filter_by(dist_id=dist_id,
#                     status="audited").all()
#     temp_data = []
#     current_counter = 0
#     for results in data:
#         sku_data = {}
#         if len(temp_data) == 0:
#             sku_data["bag_id"] = results[0]
#             bag_obj = bag.query.filter_by(id=sku_data["bag_id"]).first()
#             sku_data["bag_weight"] = bag_obj.weight
#             sku_data["bag_uid"] = bag_obj.uid
#             sku_data["bag_status"] = bag_obj.status
#             sku_obj = auditsku.query.filter_by(id=results[1]).first()
#             sku_obj_data = sku.query.filter_by(id=sku_obj.sku_id).first()
#             temp_sku = {
#                 "audit_sku_id" : sku_obj.sku_id,
#                 "sku_id" : sku_obj_data.id,
#                 "sku_name" : sku_obj_data.name,
#                 "sku_weight" : sku_obj_data.description

#             }
#             sku_data["sku_data"] = [temp_sku]
            
#             temp_data.append(sku_data)
#         else:
#             if results[0] in temp_data[current_counter].values():
#                 sku_obj = auditsku.query.filter_by(id=results[1]).first()
#                 sku_obj_data = sku.query.filter_by(id=sku_obj.sku_id).first()
#                 temp_sku = {
#                     "audit_sku_id" : sku_obj.sku_id,
#                     "sku_id" : sku_obj_data.id,
#                     "sku_name" : sku_obj_data.name,
#                     "sku_weight" : sku_obj_data.description

#                 }
#                 sku_data["sku_data"] = [temp_sku]
              
#                 temp_data[current_counter]["sku_data"].append(temp_sku)
#             elif results[0] not in temp_data[current_counter].values():
#                 sku_data = {}
#                 sku_data["bag_id"] = results[0]
                
#                 bag_obj = bag.query.filter_by(id=results[0]).first()
#                 sku_data["bag_weight"] = bag_obj.weight
#                 sku_data["bag_uid"] = bag_obj.uid
#                 sku_data["bag_status"] = bag_obj.status
#                 sku_obj = auditsku.query.filter_by(id=results[1]).first()
#                 sku_obj_data = sku.query.filter_by(id=sku_obj.sku_id).first()
#                 temp_sku = {
#                     "audit_sku_id" : sku_obj.sku_id,
#                     "sku_id" : sku_obj_data.id

#                 }
#                 sku_data["sku_data"] = [temp_sku]
#                 temp_data.append(sku_data)
#                 current_counter += 1


#         # temp_bag_id = results[0]
#         # temp_sku_id = results[1]
#         # sku_data = {}
#         # current_counter = 0
#         print(len(temp_data))
#     return jsonify(temp_data)




@blueprint.route('/get_dist_order',methods=['GET','POST'])
def get_dist_order():
    data = request.get_json(force=True)
    dist_id = data["dist_id"]
    temp_data = []
    dist_to_bag = disttobag.query.filter_by(dist_id=data["dist_id"], status='audited').all()
    for results in dist_to_bag:
        temp_bag = {}
        bag_obj = bag.query.filter_by(id=results.bag_id).first()
        temp_bag["bag_id"] = bag_obj.id
        temp_bag["weight"] = bag_obj.weight
        temp_bag["bag_uid"] = bag_obj.uid
        temp_bag["status"] = bag_obj.status
        temp_bag["sku_data"] = []
        sku_obj = bagtosku.query.filter_by(bag_id=bag_obj.id).all()
        for item in sku_obj:
            audit_sku = auditsku.query.filter_by(id=item.sku_id).first()
            temp_sku = {}
            sku_obj = sku.query.filter_by(id=audit_sku.sku_id).first()
            temp_sku["sku_id"] = sku_obj.id
            temp_sku["name"] = sku_obj.name
            temp_sku["description"] = sku_obj.description
            temp_sku["asn_code"] = audit_sku.asn_code
            temp_sku["weight"] = audit_sku.weight
            temp_bag["sku_data"].append(temp_sku)
        temp_data.append(temp_bag)
    return jsonify(temp_data)




def create_pickup_number():
    message = '1' #encrypted message
    LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    for key in range(len(LETTERS)):
        translated = ''
        for symbol in message:
            if symbol in LETTERS:
                num = LETTERS.find(symbol)
                num = num - key
                if num < 0:
                    num = num + len(LETTERS)
                translated = translated + LETTERS[num]
            else:
                translated = translated + symbol
    print('Hacking key #%s: %s' % (key, translated))

# create pickup object and map it to bag
@blueprint.route('/create_pickup',methods=["GET","POST"])
def create_pickup():
    import string
    import random
    data = request.get_json(force=True)
    transporter_id = data["transporter_id"]
    truck_number = data["truck_number"]
    latitude = data["latitude"]
    longnitude = data["longnitude"]
    dist_id = data["dist_id"]
    bag_data = data["bag_data"]
    # hash = create_pickup_number()
    # need to create pickup number
    pickup_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))    
    pickup_obj = pickup(transporter_id=transporter_id,truck_number=truck_number,latitude=latitude,longnitude=longnitude,
                        dist_id=dist_id,pickup_number=pickup_number,created_at=datetime.datetime.now())
    db.session.add(pickup_obj)
    db.session.commit()
    for bag_id in bag_data:
        pick_bag_obj = picktobag(bag_id=bag_id["bag_id"],pick_id=pickup_obj.id,
                                status=bag_id["status"],created_at=datetime.datetime.now())
        db.session.add(pick_bag_obj)
        db.session.commit()
        temp_bag_obj = bag.query.filter_by(id=bag_id["bag_id"]).first()
        temp_bag_obj.status = "picked"
        db.session.commit()
    # raise ValueError([transporter_id,truck_number,latitude,longnitude,
    # dist_id, bag_data])
    return 'true'



pickup_object = {
    "transporter_id" : "8",
    "truck_number" : "12345",
    "latitude" : "23.32",
    "longnitude" : "23.78",
    "dist_id" : "3",
    "bag_data" : [
        {
            "bag_id" : "190",
            "status" : "picked"

        },
        {
            "bag_id" : "191",
            "status" : "picked"
            
        },
        {
            "bag_id" : "192",
            "status" : "picked"
            
        },
        {
            "bag_id" : "193",
            "status" : "incorrect"
            
        }
    
    ]

}


@blueprint.route('/delete',methods=["GET","POST"])
def delete():
    audit.query.delete()
    db.session.commit()
    return "data deleted"