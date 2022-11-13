from email import message


# from sympy import residue
from app import transporter
from tabulate import tabulate
from app.depo import blueprint
from flask_restful import Resource, Api
from flask import jsonify, render_template, redirect, request, url_for
import json
from app.base.util import verify_pass
from app.models import audit, bag, depotomaster, depovendor, sku, auditsku, bagtosku, audittobag, disttobag, pickup, picktobag, deviatedbag, userinfo
from app import db
from app.models import depoinventory, deviateddepobag, depopickup
import datetime

from app import mail

from flask_mail import Message

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
        if pickup_obj.status == "collected":
            return jsonify(status=300,message="pickup already collected!")
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
        return jsonify(status=200,pickup_data=temp_data,message="pickup data delievered!")
    else:
        return jsonify(status=500,pickup_data=temp_data,message="no data for pickup!")



# get bags data mapped with LR number

@blueprint.route('/get_lr_number_order',methods=['GET','POST'])
def get_lr_number_order():
    data = request.get_json(force=True)
    lr_number = data["lr_number"]
    temp_data = []
    pickup_obj = pickup.query.filter_by(lr_number=lr_number).first()
    if pickup_obj is not None:
        if pickup_obj.status == "collected":
            return jsonify(status=300,message="pickup already collected!")
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
        return jsonify(status=200,pickup_data=temp_data,message="pickup data delievered!")
    else:
        return jsonify(status=500,pickup_data=temp_data,message="no data for pickup!")


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
                "remarks" : "weight is less",
                "imageURL":"https://s3.ap-south-1.amazonaws.com/mondelez.in/new_user_credentials.csv"
            }

        }
    
    ]
    

}
            

def send_email(html):

    msg = Message("Bag Marked deviated by Depo Master",
                  recipients=["sharma.abhi1114@gmail.com"])
    # msg.recipients = [""]
    # msg.add_recipient("sharma.abhi1114@gmail.com")
    msg.html = html
    mail.send(msg)
    print("mail sent")



            
@blueprint.route('/submit_pickup',methods=['GET','POST'])
def submit_pickup():
    data = request.get_json(force=True)
    pickup_number = data["pickup_number"]
    depo_master_id = data["depo_master_id"]
    depo_id = data["depo_id"]
    latitude = data["latitude"]
    longnitude = data["longnitude"]
    bag_data = data["bag_data"]
    table_headings = [["Bag UID", "Actual Weight", "New Weight", "Depo Master", "Depo Name"]]
    try:
        exist_pickup_obj  = pickup.query.filter_by(pickup_number=pickup_number).first()
        if exist_pickup_obj is not None:
            if exist_pickup_obj.status == "collected":
                return jsonify(status=500,message="pickup already saved")
    except Exception as e:
        print(e)
        return jsonify(status=500,message="no pickup found")
    try:
        depo_master_obj = userinfo.query.filter_by(id=depo_master_id).first()
        depo_master_name = depo_master_obj.name
    except Exception as e:
        print(e)
        return jsonify(status=500,message="no depo master found")
    try:
        depo_obj = depovendor.query.filter_by(id=depo_id).first()
        depo_name = depo_obj.vendor_name
    except Exception as e:
        print(e)
        return jsonify(status=500,message="no depo found")
    if bag is not None and len(bag_data) !=0:
        for temp_bag in bag_data:
            if temp_bag["status"] == "incorrect":
                try:
                    submit_obj = depoinventory(depo_id=depo_id,bag_id=temp_bag["bag_id"],status="collected",latitude=latitude,
                                            longnitude=longnitude,created_at=datetime.datetime.now(),
                                            submitted_by=depo_master_id)
                    deviated_data = temp_bag["deviated_data"]
                    deviated_bag_obj = deviateddepobag(bag_id=temp_bag["bag_id"],weight=deviated_data["weight"],
                                                remarks=deviated_data["remarks"], created_at=datetime.datetime.now()
                                                ,image_url=deviated_data["imageURL"])
                    db.session.add(submit_obj)
                    db.session.add(deviated_bag_obj)
                    bag_obj = bag.query.filter_by(id=temp_bag["bag_id"]).first()
                    bag_obj.status = "collected"
                    new_weight = deviated_data["weight"]
                    actual_weight = bag_obj.weight
                    table_headings.append([bag_obj.uid,actual_weight, new_weight, depo_master_name,depo_name])
                    # content = """
                    #             <th>{0}</th>
                    #             <th>{1}</th>
                    #             <th>{2}</th>
                    #             <th>{3}</th>
                    #             <th>{4}</th>
                    #         """.format(bag_obj.uid,actual_weight, new_weight, depo_master_name,depo_name)
                    # temp += content
                    # temp = '\n'.join([temp, content])
                except Exception as e:
                    print(e)
                    db.session.rollback()
                    db.session.close()
                    return jsonify(status=500,message="no data to save")
                
            else:
                try:
                    bag_obj = bag.query.filter_by(id=temp_bag["bag_id"]).first()
                    if temp_bag["bag_weight"] != bag_obj.weight:
                        db.session.rollback()
                        db.session.close()
                        return jsonify(status=500,message="no data to save")
                    submit_obj = depoinventory(depo_id=depo_id,bag_id=temp_bag["bag_id"],status="collected",latitude=latitude,
                                            longnitude=longnitude,created_at=datetime.datetime.now(),
                                            submitted_by=depo_master_id)
                    db.session.add(submit_obj)
                    bag_obj.status = "collected"
                except Exception as e:
                    print(e)
                    db.session.rollback()
                    db.session.close()
                    return jsonify(status=500,message="no data to save")
        try:        
            pickup_obj = pickup.query.filter_by(pickup_number=pickup_number).first()
            pickup_obj.status = "collected"
            db.session.commit()
            send_email(tabulate(table_headings, tablefmt='html'))
            return jsonify(status=200,message="pickup saved successfully!")
        except Exception as e:
            print(e)
            db.session.rollback()
            db.session.close()
            return jsonify(status=500,message="no data to save")
            
    else:
        return jsonify(status=500,message="no data to save")



# get asn number data will be as same as destruction centre


# create pickup in depo with asn number


depo_asn_object = {

    "asn_number" : "ASN00MND00TNT12",
    "depo_master_id" : "14",
    "depo_id" : "2",
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
            "bag_id" : "179",
            "bag_weight" : "25",
            "status": "correct",
            "deviated_data" : ""

        },
        {
            "bag_id" : "180",
            "bag_weight" : "25",
            "status": "correct",
            "deviated_data" : ""

        },
        {
            "bag_id" : "178",
            "bag_weight" : "25",
            "status": "incorrect",
            "deviated_data" : {
                "weight" : "15",
                "remarks" : "weight is less"
            }

        }
    
    ]
    

}


@blueprint.route('/submit_asn_pickup',methods=['GET','POST'])
def submit_asn_pickup():
    data = request.get_json(force=True)
    asn_number = data["asn_number"]
    depo_master_id = data["depo_master_id"]
    depo_id = data["depo_id"]
    latitude = data["latitude"]
    longnitude = data["longnitude"]
    bag_data = data["bag_data"]
    table_headings = [["Bag UID", "Actual Weight", "New Weight", "Depo Master", "Depo Name"]]
    try:
        depo_master_obj = userinfo.query.filter_by(id=depo_master_id).first()
        depo_master_name = depo_master_obj.name
    except Exception as e:
        print(e)
        return jsonify(status=500,message="no depo master found")
    try:
        depo_obj = depovendor.query.filter_by(id=depo_id).first()
        depo_name = depo_obj.vendor_name
    except Exception as e:
        print(e)
        return jsonify(status=500,message="no depo found")
    try:
        exist_pickup_obj = depopickup.query.filter_by(asn_number=asn_number).first()
        if exist_pickup_obj is not None:
            if exist_pickup_obj.status == "collected":
                return jsonify(status=500,message="pickup already saved!")
            if exist_pickup_obj.status == "submitted":
                return jsonify(status=500,message="pickup already saved!")
    except Exception as e:
        print(e)
        return jsonify(status=500,message="no data to save")
    if bag is not None and len(bag_data) !=0:
        for temp_bag in bag_data:
            try:
                if temp_bag["status"] == "incorrect":
                    try:
                        prev_bag_obj = depoinventory.query.filter_by(bag_id=temp_bag["bag_id"]).first()
                        if prev_bag_obj is not None:
                            if str(prev_bag_obj.depo_id) == depo_id:
                                return jsonify(status=500, message="can not save")
                            else:
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
                                table_headings.append([bag_obj.uid,bag_obj.weight, deviated_data["weight"], depo_master_name,depo_name])
                        else:
                            db.session.rollback()
                            db.session.close()
                            return jsonify(status=500,message="no data to save")       
                    except Exception as e:
                        print(e)
                        db.session.rollback()
                        db.session.close()
                      
                        return jsonify(status=500,message="no data to save")
                else:
                    try:
                        prev_bag_obj = depoinventory.query.filter_by(bag_id=temp_bag["bag_id"]).first()
                        if prev_bag_obj is not None:
                            if str(prev_bag_obj.depo_id) != depo_id:
                                submit_obj = depoinventory(depo_id=depo_id,bag_id=temp_bag["bag_id"],status="collected",latitude=latitude,
                                                            longnitude=longnitude,created_at=datetime.datetime.now(),
                                                            submitted_by=depo_master_id)
                                db.session.add(submit_obj)
                                bag_obj = bag.query.filter_by(id=temp_bag["bag_id"]).first()
                                bag_obj.status = "collected"
                            else:
                                db.session.rollback()
                                db.session.close()
                                return jsonify(status=500, message="can not save")
                    except Exception as e:
                        print(e)
                        db.session.rollback()
                        db.session.close()
                        
                        return jsonify(status=500,message="no data to save")

            except Exception as e:
                 print(e) 

        try:
            pickup_obj = depopickup.query.filter_by(asn_number=asn_number).first()
            pickup_obj.status = "submitted"
            db.session.commit()
            send_email(tabulate(table_headings, tablefmt='html'))
            return jsonify(status=200,message="pickup saved successfully!")
        except Exception as e:
            print(e)
            db.session.rollback()
            db.session.close()
    else:
        return jsonify(status=500,message="no data to save")



# if an depo master could associate with multiple depos.

# @blueprint.route('/get_depo',methods=['GET','POST'])
# def get_depo():
#     data = request.get_json(force=True)
#     depo_master_id = data["depo_master_id"]
#     depo_master_data = depotomaster.query.filter_by(user_id=depo_master_id).first()
#     depo_data = []
#     if len(depo_master_data) != 0:
#         for depo_master in depo_master_data:
#             temp = {}
#             depo_obj = depovendor.query.filter_by(id=depo_master.vendor_id).first()
#             temp["depo_id"] = depo_obj.id
#             temp["depo_name"] = depo_obj.vendor_name
#             temp["depo_code"] = depo_obj.vendor_code
#             depo_data.append(temp)
#         return jsonify(status=200,depo_data=depo_data,message="depo data delieverd!")

#     else:

#         return jsonify(status=500,message="empty depo data")


# if an depo master can be assigned to only one depo
@blueprint.route('/get_depo',methods=['GET','POST'])
def get_depo():
    data = request.get_json(force=True)
    depo_master_id = data["depo_master_id"]
    depo_master_data = depotomaster.query.filter_by(user_id=depo_master_id).first()
    depo_data=[]
    if depo_master_data is not None:
        temp = {}
        depo_obj = depovendor.query.filter_by(id=depo_master_data.vendor_id).first()
        temp["depo_id"] = depo_obj.id
        temp["depo_name"] = depo_obj.vendor_name
        temp["depo_code"] = depo_obj.vendor_code
        temp["latitude"] = depo_obj.latitude
        temp["longnitude"] = depo_obj.longnitude
        depo_data.append(temp)
        return jsonify(status=200,depo_data=depo_data,message="depo data delieverd!")
    else:
        return jsonify(status=500,message="empty depo data")




# submit bag objects directly in depo with submit bag button


save_bag_obj = {
    "truck_number" : "12345",
    "depo_master_id" : "14",
    "depo_id" : "1",
    "latitude" : "30.85",
    "longnitude" : "75.85",
    "bag_data" : [
        {
            "bag_id": "227",
            "bag_weight": "5",
            "status": "incorrect",
            "deviated_data": {
                "weight": "2",
                "remarks": "The actual weight is only 2 kg,"
            }
        },
        {
            "bag_id": "228",
            "bag_weight": "25",
            "status": "correct",
            "deviated_data": ""
        },
        {
            "bag_id": "229",
            "bag_weight": "0",
            "status": "incorrect",
            "deviated_data": {
                "weight": "12",
                "remarks": "test kr lungi mujhe bhi mila hai kya hua hai"
            }
        },
        {
            "bag_id": "215",
            "bag_weight": "5",
            "status": "incorrect",
            "deviated_data": {
                "weight": "2",
                "remarks": "The actual weight is only 2 kg,"
            }
        },
        {
            "bag_id": "216",
            "bag_weight": "25",
            "status": "correct",
            "deviated_data": ""
        },
        {
            "bag_id": "217",
            "bag_weight": "0",
            "status": "incorrect",
            "deviated_data": {
                "weight": "12",
                "remarks": "test kr lungi mujhe bhi mila hai kya hua hai"
            }
        }
    
    ]

}





# @blueprint.route('/submit_direct_pickup',methods=['GET','POST'])
# def submit_direct_pickup():
#     data = request.get_json(force=True)
#     depo_master_id = data["depo_master_id"]
#     depo_id = data["depo_id"]
#     bag_data = data["bag_data"]
#     latitude = data["latitude"]
#     longnitude = data["longnitude"]
#     truck_number = data["truck_number"]
#     seperate_bag_data = get_seperate_bag_data(bag_data)
#     table_headings = [["Bag UID", "Actual Weight", "New Weight", "Depo Master", "Depo Name"]]
#     truck_number =get_strip_truck_number(truck_number)
#     try:
#         depo_master_obj = userinfo.query.filter_by(id=depo_master_id).first()
#         depo_master_name = depo_master_obj.name
#     except Exception as e:
#         print(e)
#         return jsonify(status=500,message="no depo master found")
#     try:
#         depo_obj = depovendor.query.filter_by(id=depo_id).first()
#         depo_name = depo_obj.vendor_name
#     except Exception as e:
#         print(e)
#         return jsonify(status=500,message="no depo found")
#     if len(seperate_bag_data.values()) != 0:
#         for key, value in seperate_bag_data.items():
#             temp_truck_obj = pickup.query.filter_by(id=key).first()
#             if temp_truck_obj.truck_number == truck_number:
#                 temp_pickup_obj = picktobag.query.filter_by(pick_id=key).count()
#                 print(temp_pickup_obj, len(value))
#                 if temp_pickup_obj == len(value):
#                     for temp_bag in value:
#                         if temp_bag["status"] == "incorrect":
#                             try:
#                                 submit_obj = depoinventory(depo_id=depo_id,bag_id=temp_bag["bag_id"],status="collected",latitude=latitude,
#                                                         longnitude=longnitude,created_at=datetime.datetime.now(),
#                                                         submitted_by=depo_master_id)
#                                 deviated_data = temp_bag["deviated_data"]
#                                 deviated_bag_obj = deviateddepobag(bag_id=temp_bag["bag_id"],weight=deviated_data["weight"],
#                                                             remarks=deviated_data["remarks"], created_at=datetime.datetime.now()
#                                                             ,image_url=deviated_data["imageURL"])
#                                 db.session.add(submit_obj)
#                                 db.session.add(deviated_bag_obj)
#                                 bag_obj = bag.query.filter_by(id=temp_bag["bag_id"]).first()
#                                 bag_obj.status = "collected"
#                                 new_weight = deviated_data["weight"]
#                                 actual_weight = bag_obj.weight
#                                 table_headings.append([bag_obj.uid,actual_weight, new_weight, depo_master_name,depo_name])
#                             except Exception as e:
#                                 print(e)
#                                 db.session.rollback()
#                                 db.session.close()
#                                 return jsonify(status=500,message="no data to save")
                            
#                         else:
#                             try:
#                                 bag_obj = bag.query.filter_by(id=temp_bag["bag_id"]).first()
#                                 if temp_bag["bag_weight"] != bag_obj.weight:
#                                     db.session.rollback()
#                                     db.session.close()
#                                     return jsonify(status=500,message="no data to save")
#                                 submit_obj = depoinventory(depo_id=depo_id,bag_id=temp_bag["bag_id"],status="collected",latitude=latitude,
#                                                         longnitude=longnitude,created_at=datetime.datetime.now(),
#                                                         submitted_by=depo_master_id)
#                                 db.session.add(submit_obj)
#                                 bag_obj.status = "collected"
#                             except Exception as e:
#                                 print(e)
#                                 db.session.rollback()
#                                 db.session.close()
#                                 return jsonify(status=500,message="no data to save")
                    
#                 else:
#                     return jsonify(status=500,message="bag count missing")
#                 temp_pick_object = pickup.query.filter_by(id=key).first()
#                 print(temp_pick_object.id, key)
#                 temp_pick_object.status = "collected"
#                 send_email(tabulate(table_headings, tablefmt='html'))
#             else:
#                 return jsonify(status=500,message="truck number mismatch")
#         db.session.commit()
#         return jsonify(status=200,message="bags saved successfully")
#     else:
#         return jsonify(status=500,message="bag count missing") 




# changing to remove the truck number for direct submit

new_save_bag_obj = {
    "depo_master_id" : "14",
    "depo_id" : "1",
    "latitude" : "30.85",
    "longnitude" : "75.85",
    "bag_data" : [
        {
            "bag_id": "227",
            "bag_weight": "5",
            "status": "incorrect",
            "deviated_data": {
                "weight": "2",
                "remarks": "The actual weight is only 2 kg,"
            }
        },
        {
            "bag_id": "228",
            "bag_weight": "25",
            "status": "correct",
            "deviated_data": ""
        },
        {
            "bag_id": "229",
            "bag_weight": "0",
            "status": "incorrect",
            "deviated_data": {
                "weight": "12",
                "remarks": "test kr lungi mujhe bhi mila hai kya hua hai"
            }
        },
        {
            "bag_id": "215",
            "bag_weight": "5",
            "status": "incorrect",
            "deviated_data": {
                "weight": "2",
                "remarks": "The actual weight is only 2 kg,"
            }
        },
        {
            "bag_id": "216",
            "bag_weight": "25",
            "status": "correct",
            "deviated_data": ""
        },
        {
            "bag_id": "217",
            "bag_weight": "0",
            "status": "incorrect",
            "deviated_data": {
                "weight": "12",
                "remarks": "test kr lungi mujhe bhi mila hai kya hua hai"
            }
        }
    
    ]

}


def get_seperate_bag_data(bag_data):
    temp_data = bag_data
    pickup_data = {}
    try:
        for temp_bag in temp_data:
            pickup_obj = picktobag.query.filter_by(bag_id=temp_bag["bag_id"]).first()
            if pickup_obj is None:
                pass
            if pickup_obj is not None:
                if pickup_obj.pick_id not in pickup_data.keys():
                    pickup_data[pickup_obj.pick_id] = [temp_bag]
                else:
                    pickup_data[pickup_obj.pick_id].append(temp_bag)
        return pickup_data
    except Exception as e:
        print(e)
        return pickup_data

def get_strip_truck_number(truck_number):
    new_truck_number = truck_number.replace(" ", "").lower()
    return new_truck_number    


@blueprint.route('/submit_direct_pickup',methods=['GET','POST'])
def submit_direct_pickup():
    import json
    data = request.get_json(force=True)
    depo_master_id = data["depo_master_id"]
    depo_id = data["depo_id"]
    bag_data = data["bag_data"]
    latitude = data["latitude"]
    longnitude = data["longnitude"]
    table_headings = [["Bag UID", "Actual Weight", "New Weight", "Depo Master", "Depo Name"]]
    is_deviation = False
    print("depo request")
    print(json.dumps(data))
    try:
        seperate_bag_data = get_seperate_bag_data(bag_data)
        print("below is seperated data!")
        print(seperate_bag_data)
    except Exception as e:
        print(e)
        return jsonify(status=500,message="Wrong pickup data")
    try:
        depo_master_obj = userinfo.query.filter_by(id=depo_master_id).first()
        depo_master_name = depo_master_obj.name
    except Exception as e:
        print(e)
        return jsonify(status=500,message="no depo master found")
    try:
        depo_obj = depovendor.query.filter_by(id=depo_id).first()
        depo_name = depo_obj.vendor_name
    except Exception as e:
        print(e)
        return jsonify(status=500,message="no depo found")
    if len(seperate_bag_data.values()) != 0:
        for key, value in seperate_bag_data.items():
            for temp_bag in value:
                if temp_bag["status"] == "incorrect":
                    try:
                        submit_obj = depoinventory(depo_id=depo_id,bag_id=temp_bag["bag_id"],status="collected",latitude=latitude,
                                                longnitude=longnitude,created_at=datetime.datetime.now(),
                                                submitted_by=depo_master_id)
                        deviated_data = temp_bag["deviated_data"]
                        deviated_bag_obj = deviateddepobag(bag_id=temp_bag["bag_id"],weight=deviated_data["weight"],
                                                    remarks=deviated_data["remarks"], created_at=datetime.datetime.now()
                                                    ,image_url=deviated_data["imageURL"])
                        db.session.add(submit_obj)
                        db.session.add(deviated_bag_obj)
                        bag_obj = bag.query.filter_by(id=temp_bag["bag_id"]).first()
                        bag_obj.status = "collected"
                        new_weight = deviated_data["weight"]
                        actual_weight = bag_obj.weight
                        table_headings.append([bag_obj.uid,actual_weight, new_weight, depo_master_name,depo_name])
                        if is_deviation ==  False:
                            is_deviation = True
                    except Exception as e:
                        print(e)
                        db.session.rollback()
                        db.session.close()
                        return jsonify(status=500,message="no data to save first")
                    
                else:
                    try:
                        bag_obj = bag.query.filter_by(id=temp_bag["bag_id"]).first()
                        if temp_bag["bag_weight"] != bag_obj.weight:
                            db.session.rollback()
                            db.session.close()
                            return jsonify(status=500,message="right bag weight mismatch")
                        submit_obj = depoinventory(depo_id=depo_id,bag_id=temp_bag["bag_id"],status="collected",latitude=latitude,
                                                longnitude=longnitude,created_at=datetime.datetime.now(),
                                                submitted_by=depo_master_id)
                        db.session.add(submit_obj)
                        bag_obj.status = "collected"
                    except Exception as e:
                        print(e)
                        db.session.rollback()
                        db.session.close()
                        return jsonify(status=500,message="no data to save second")
                    
            # else:
            #     return jsonify(status=500,message="pickup bag count mismatch")
            # get the total number of bags for pickupid
            try:
                total_pickup_obj = picktobag.query.filter_by(pick_id=key).all()
                if total_pickup_obj is not None:
                    total_pickup_bag = len(total_pickup_obj)
                    collected_count = 0
                    for temp_bag in total_pickup_obj:
                        temp_bag_obj = bag.query.filter_by(id=temp_bag.bag_id).first()
                        if temp_bag_obj.status == "collected":
                            collected_count += 1
                    bag_difference = total_pickup_bag - collected_count
                    if bag_difference == 0:
                        temp_pick_object = pickup.query.filter_by(id=key).first()
                        temp_pick_object.status = "collected"
            except Exception as e:
                print(e)
                print("error while checking pickup status")
            # print(temp_pick_object.id, key)
            
            if is_deviation:
                try:
                    send_email(tabulate(table_headings, tablefmt='html'))
                except Exception as e:
                    print(e)
                    print("Error in sending email")
        db.session.commit()
        
        return jsonify(status=200,message="{0}, Bags successfully submitted!".format(depo_master_name.capitalize()))
    else:
        return jsonify(status=500,message="Bags are not picked yet!") 


