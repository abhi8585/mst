from email import message
from operator import sub
from re import M
from app import transporter
from app.transporter import blueprint
from flask_restful import Resource, Api
from flask import jsonify, render_template, redirect, request, url_for
import json
from app.base.util import verify_pass
from app.models import audit, bag, sku, auditsku, bagtosku, audittobag, disttobag, pickup, picktobag, transtovendor, transportvendor, disttovendor, distvendor, userinfo
from app.models import deviatedbag
from app import db
import datetime

from app import mail

from flask_mail import Message
from tabulate import tabulate


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
    dist_to_bag = disttobag.query.filter_by(dist_id=data["dist_id"], status='audited').count()
    if dist_to_bag != 0:
        return jsonify(status=200,order_count = dist_to_bag)
    else:
        return jsonify(status=500,order_count=0)
    # for results in dist_to_bag:
    #     temp_bag = {}
    #     bag_obj = bag.query.filter_by(id=results.bag_id).first()
    #     temp_bag["bag_id"] = bag_obj.id
    #     temp_bag["weight"] = bag_obj.weight
    #     temp_bag["bag_uid"] = bag_obj.uid
    #     temp_bag["status"] = bag_obj.status
    #     temp_bag["sku_data"] = []
    #     sku_obj = bagtosku.query.filter_by(bag_id=bag_obj.id).all()
    #     for item in sku_obj:
    #         audit_sku = auditsku.query.filter_by(id=item.sku_id).first()
    #         temp_sku = {}
    #         sku_obj = sku.query.filter_by(id=audit_sku.sku_id).first()
    #         temp_sku["sku_id"] = sku_obj.id
    #         temp_sku["name"] = sku_obj.name
    #         temp_sku["description"] = sku_obj.description
    #         temp_sku["asn_code"] = audit_sku.asn_code
    #         temp_sku["weight"] = audit_sku.weight
    #         temp_bag["sku_data"].append(temp_sku)
    #     temp_data.append(temp_bag)
    # return jsonify(temp_data)


@blueprint.route('/get_bag_data',methods=['POST'])
def get_bag_data():
    data = request.get_json(force=True)
    bag_uid = data["bag_uid"]
    bag_data = bag.query.filter_by(uid=bag_uid).first()
    if bag_data is not None:
        bag_sku = bagtosku.query.filter_by(bag_id = bag_data.id).all()
        temp = dict(bag_weight=bag_data.weight,bag_id=bag_data.id,bag_status = bag_data.status,sku_data=[])
    
        for audit_sku in bag_sku:
            audit_sku_id = auditsku.query.filter_by(id=audit_sku.sku_id).first()
            sku_obj = sku.query.filter_by(id=audit_sku_id.sku_id).first()
            if sku_obj is not None:
                temp_sku = dict(audit_sku_id=audit_sku_id.id,sku_id=sku_obj.id,sku_weight=audit_sku_id.weight
                    ,sku_asn_code=audit_sku_id.asn_code,name=sku_obj.name,description=sku_obj.description)
                temp["sku_data"].append(temp_sku)
        return jsonify(status=200,bag_data=temp)
    else:
        return jsonify(status=500,bag_data=[])




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



def send_email(html):

    msg = Message("Bag Marked deviated by Transporter",
                  sender="abhi.sharma1114@gmail.com",
                  recipients=["sharma.abhi1114@gmail.com"])
    # msg.recipients = [""]
    # msg.add_recipient("sharma.abhi1114@gmail.com")
    msg.html = html
    mail.send(msg)
    print("mail sent")



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
    table_headings = [["Bag UID", "Actual Weight", "New Weight", "Transporter", "Distributor"]]
    # hash = create_pickup_number()
    # need to create pickup number
    # pickup_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))
    
    # get transporter name
    try:
        trans_obj = userinfo.query.filter_by(id=transporter_id).first()
        transporter_name = trans_obj.name
    except Exception as e:
        print(e)
        return jsonify(status=500, message="no transporter found")
   
    # get distributor name

    try:
        dist_obj = distvendor.query.filter_by(id=dist_id).first()
        dist_name = dist_obj.vendor_name
    except Exception as e:
        print(e)
        return jsonify(status=500, message="no distributor found")

    pickup_number = pickup.query.count() + 1
    pickup_number = "PCK00MND00TNT{0}".format(pickup_number)
    try:
        pickup_obj = pickup(transporter_id=transporter_id,truck_number=truck_number,latitude=latitude,longnitude=longnitude,
                            dist_id=dist_id,pickup_number=pickup_number,status="picked",created_at=datetime.datetime.now())
        db.session.add(pickup_obj)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        db.session.close()
        return jsonify(status=500,message="pickup can not save")
    if len(bag_data) != 0:
        for bag_id in bag_data:
            if bag_id["deviated_data"] != "" and bag_id["status"] == "incorrect":
                try:
                    temp = bag_id["deviated_data"]
                    deviate_bag = deviatedbag(bag_id=bag_id["bag_id"],weight=temp["weight"],
                                            remarks=temp["remarks"],created_at=datetime.datetime.now())
                    pick_bag_obj = picktobag(bag_id=bag_id["bag_id"],pick_id=pickup_obj.id,
                                        status=bag_id["status"],created_at=datetime.datetime.now())
                    db.session.add(pick_bag_obj)
                    db.session.add(deviate_bag)
                    temp_bag_obj = bag.query.filter_by(id=bag_id["bag_id"]).first()
                    temp_bag_obj.status = "picked"
                    temp_dist_bag = disttobag.query.filter_by(bag_id=bag_id["bag_id"]).first()
                    temp_dist_bag.status = "picked"
                    actual_weight = temp_bag_obj.weight
                    new_weight = bag_id["deviated_data"]["weight"]
                    table_headings.append([temp_bag_obj.uid,actual_weight,new_weight,transporter_name,dist_name])
                    

                except Exception as e:
                    print(e)
                    db.session.rollback()
                    db.session.close()
                    return jsonify(status=500,message="bag data can not be saved")
                
            else:
                # temp_bag = bag_id
                temp_bag_obj = bag.query.filter_by(id=bag_id["bag_id"]).first()
                try:
                        if temp_bag_obj.weight == bag_id["bag_weight"]:
                            pick_bag_obj = picktobag(bag_id=bag_id["bag_id"],pick_id=pickup_obj.id,
                                            status=bag_id["status"],created_at=datetime.datetime.now())
                            db.session.add(pick_bag_obj)
                            temp_bag_obj.status = "picked"
                            temp_dist_bag = disttobag.query.filter_by(bag_id=bag_id["bag_id"]).first()
                            temp_dist_bag.status = "picked"
                        
                        else:
                            db.session.rollback()
                            db.session.close()
                            return jsonify(status=500,message="bag data mismatch!")
                except Exception as e:
                    print(e)
                    db.session.rollback()
                    db.session.close()
                    return jsonify(status=500,message="bag data can not be saved")

        db.session.commit()
        send_email(tabulate(table_headings, tablefmt='html'))
        return jsonify(status=200,pickup_number = pickup_number,message="pickup saved successfully!")
    else:
        db.session.rollback()
        db.session.close()
        return jsonify(status=500,message="no bag data to store!")
    
    #     # temp_bag_obj.status = "picked"
    #     # db.session.commit()
    # # raise ValueError([transporter_id,truck_number,latitude,longnitude,
    # # dist_id, bag_data])
    # return 'true'



pickup_object = {
    "transporter_id" : "11",
    "truck_number" : "12345",
    "latitude" : "23.32",
    "longnitude" : "23.78",
    "dist_id" : "3",
    "bag_data" : [
        {
            "bag_id" : "1",
            "bag_weight" : "25",
            "status": "correct",
            "deviated_data" : "",

        },
        {
            "bag_id" : "2",
            "bag_weight" : "25",
            "status": "correct",
            "deviated_data" : "",

        },
        {
            "bag_id" : "3",
            "bag_weight" : "25",
            "status": "correct",
            "deviated_data" : "",

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

@blueprint.route('/get_transport_distributor', methods=['POST'])
def get_transport_distributor():
    data = request.get_json(force=True)
    user_id = data["user_id"]
    auditor_data = get_auditor_dist(user_id)
    if auditor_data:
        temp = {
            "distributors" : auditor_data
        }
        return jsonify(status=200,distributors=auditor_data)
    return jsonify(status=500,distributors=[])


@blueprint.route('/get_transport_pickup', methods=['POST'])
def get_transport_pickup():
    data = request.get_json(force=True)
    transporter_id = data["transporter_id"]
    pickup_obj = pickup.query.filter_by(transporter_id=transporter_id, status="picked").all()
    pickup_data = []
    if pickup_obj is not None:
        for pick in pickup_obj:
            temp = {}
            bag_count = picktobag.query.filter_by(pick_id=pick.id).count()
            if bag_count > 0:
                temp["total_bag"] = bag_count
                temp["pickup_number"] = pick.pickup_number
                temp["date"] = pick.created_at
                pickup_data.append(temp)
    else:
        return jsonify(status=500,message="no pickups")
    if len(pickup_data) != 0:
        return jsonify(status=200,pickup_data=pickup_data)
    else:
        return jsonify(status=500,message="no pickup")

@blueprint.route('/delete',methods=["GET","POST"])
def delete():
    audit.query.delete()
    db.session.commit()
    return "data deleted"


