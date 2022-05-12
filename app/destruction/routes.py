from collections import UserString
from email import message
from xxlimited import new

from itsdangerous import exc
from app.destruction import blueprint
from app.base.util import hash_pass
from flask_restful import Resource, Api
from flask import jsonify, render_template, redirect, request, url_for
import json
from app.base.util import verify_pass
from app.models import audittobag, depoinventory, destructiontomaster, destructionvendor, depopickup, deviatedbag, deviateddepobag, deviateddepopickbag, depopicktobag, depovendor, disttobag, picktobag, pickup, userinfo
from app import db
import datetime

from app.models import bag, bagtosku, auditsku, sku, destructioninventory, deviateddestructionbag, userinfo, destructionvendor, audit
from flask_mail import Message
from tabulate import tabulate
from app import mail



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
    des_obj = destructionvendor(vendor_code="535490",vendor_name="Sunrays Compost",address="Banglore",city="Banglore",pin_code='312612',
                                state="Banglore",latitude='28.656139', longnitude='77.402407',contact_person = 'Aanchal',
                                contact_number='8422915773',email='aanchal.susheen@asunrayscompost.com', created_at=datetime.datetime.now())
    db.session.add(des_obj)
    db.session.commit()
    return "object created"



@blueprint.route('/map_destruction', methods=['GET', 'POST'])
def map_destruction():
    des_map_obj = destructiontomaster(vendor_id=3, user_id=48, created_at = datetime.datetime.now())
    db.session.add(des_map_obj)
    db.session.commit()
    return "object created"





# this get destruction is for when an destruction centre mapped to multiples

# @blueprint.route('/get_destruction',methods=['GET','POST'])
# def get_destruction():
#     data = request.get_json(force=True)
#     destruction_master_id = data["destruction_master_id"]
#     depo_master_data = destructiontomaster.query.filter_by(user_id=destruction_master_id).all()
#     depo_data = []
#     if len(depo_master_data) != 0:
#         for depo_master in depo_master_data:
#             temp = {}
#             depo_obj = destructionvendor.query.filter_by(id=depo_master.vendor_id).first()
#             temp["destruction_centre_id"] = depo_obj.id
#             temp["destruction_centre_name"] = depo_obj.vendor_name
#             temp["destruction_centre_code"] = depo_obj.vendor_code
#             depo_data.append(temp)
#         return jsonify(status=200,depo_data=depo_data,message="depo data delieverd!")

#     else:

#         return jsonify(status=500,depo_data=depo_data,message="empty depo data")


# when the destruction mapped to single destruction

@blueprint.route('/get_destruction',methods=['GET','POST'])
def get_destruction():
    data = request.get_json(force=True)
    destruction_master_id = data["destruction_master_id"]
    depo_master_data = destructiontomaster.query.filter_by(user_id=destruction_master_id).first()
    depo_data = []
    if depo_master_data is not None:
        temp = {}
        depo_obj = destructionvendor.query.filter_by(id=depo_master_data.vendor_id).first()
        temp["destruction_centre_id"] = depo_obj.id
        temp["destruction_centre_name"] = depo_obj.vendor_name
        temp["destruction_centre_code"] = depo_obj.vendor_code
        temp["latitude"] = depo_obj.latitude
        temp["longnitude"] = depo_obj.longnitude
        depo_data.append(temp)
        return jsonify(status=200,depo_data=depo_data,message="depo data delieverd!")

    else:

        return jsonify(status=500,depo_data=depo_data,message="empty depo data")


@blueprint.route('/get_asn_number_data',methods=['GET','POST'])
def get_asn_number_data():
    data = request.get_json(force=True)
    asn_number = data["asn_number"]
    temp_data = []
    pickup_obj = depopickup.query.filter_by(asn_number=asn_number).first()
    if pickup_obj is not None:
        # check if already reached to destruction centre
        if pickup_obj.status == "collected" : 
            return jsonify(status=500,message="This LR number is already used!")
        # check if already reached to another depo centre
        if pickup_obj.status == "submitted" :
            return jsonify(status=500,message="This LR number is already used!")
        bags_data = depopicktobag.query.filter_by(pick_id=pickup_obj.id).all()
        for results in bags_data:
            temp = {}
            if results.status == "correct":
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

def get_strip_lr_number(truck_number):
    new_lr_number = truck_number.replace(" ", "").lower()
    return new_lr_number


@blueprint.route('/get_lr_number_data',methods=['GET','POST'])
def get_lr_number_data():
    data = request.get_json(force=True)
    try:
        lr_number = data["lr_number"]
    except Exception as e:
        return jsonify(status=500,message="wrong query parameters")
    lr_number = get_strip_lr_number(lr_number)
    temp_data = []
    pickup_obj = depopickup.query.filter_by(lr_number=lr_number).first()
    try:
        if pickup_obj is not None:
        # check if already reached to destruction centre
            if pickup_obj.status == "collected" : 
                return jsonify(status=300,message="pickup already completed")
        # check if already reached to another depo centre
            if pickup_obj.status == "submitted" :
                return jsonify(status=300,message="pickup already completed")
            # making pickup summary data
            picker_id = userinfo.query.filter_by(id=pickup_obj.picker_id).first()
            picker_name = picker_id.name
            depo_id = depovendor.query.filter_by(id=pickup_obj.depo_id).first()
            depo_name = depo_id.vendor_name
            # getting bag data
            bags_data = depopicktobag.query.filter_by(pick_id=pickup_obj.id).all()
            if len(bags_data) > 0:
                # making bag summary data
                total_bag_count = len(bags_data)
                total_weight_count = 0.00
                
                for results in bags_data:
                    temp = {}
                    if results.status == "correct":
                        bag_data = bag.query.filter_by(id=results.bag_id).first()
                        # sku_data = get_sku_data(bag_data.id)
                        temp["bag_weight"] = bag_data.weight 
                        temp["bag_id"] = bag_data.id
                        temp["bag_status"] = results.status
                        temp["bag_uid"] = bag_data.uid
                        temp["bag_sku_data"] = []
                        temp_data.append(temp)
                        total_weight_count += float(bag_data.weight)
                    if results.status == "incorrect":
                        bag_data = bag.query.filter_by(id=results.bag_id).first()
                        dev_bag_obj = deviateddepopickbag.query.filter_by(bag_id=results.bag_id).first()
                        # sku_data = get_sku_data(bag_data.id)
                        temp["bag_weight"] = dev_bag_obj.weight 
                        temp["bag_id"] = bag_data.id
                        temp["bag_status"] = results.status
                        temp["bag_uid"] = bag_data.uid
                        temp["bag_sku_data"] = []
                        temp_data.append(temp)
                        total_weight_count += float(dev_bag_obj.weight)
                return jsonify(status=200,lr_data=temp_data,message="lr number data delievered!",lr_number=lr_number,
                                total_bags=total_bag_count,total_weight=total_weight_count,picked_by=picker_name,
                                picked_at=pickup_obj.created_at.strftime("%Y-%m-%d"),depo_name=depo_name)
            else:
                return jsonify(status=500,lr_data=temp_data,message="no bag found for this pickup!",lr_number=lr_number)
        else:
            return jsonify(status=500,lr_data=temp_data,message="Wrong LR number!",lr_number=lr_number)
    except Exception as e:
        print(e)
        return jsonify(status=500,asn_data=temp_data,message="server error!",lr_number="")


# get bag data will be as same as from trasnporter


# submit pickup at destruction centre


destruction_object = {

    "lr_number" : "ASN00MND00TNT8",
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
                "remarks" : "weight is less",
                 "imageURL":"https://s3.ap-south-1.amazonaws.com/mondelez.in/new_user_credentials.csv"
            }

        }
    
    ]
    

}


def send_email(html):
    try:
        msg = Message("Bag Marked deviated by Destruction Master",
                  recipients=["sharma.abhi1114@gmail.com"])
        msg.html = html
        mail.send(msg)
        print("mail sent")
    except Exception as e:
        print(e)


def get_strip_lr_number(lr_number):
    new_lr_number = lr_number.replace(" ", "").lower()
    return new_lr_number 
    

# submit lr pickup

@blueprint.route('/submit_lr_pickup',methods=['GET','POST'])
def submit_lr_pickup():
    try:
        data = request.get_json(force=True)
        lr_number = data["lr_number"]
        # deviated_weight = data["deviated_weight"]commenting this because key from UI is not integrated giving a static weight so it can work atleast
        deviated_weight = "10.00"
        destruction_master_id = data["destruction_master_id"]
        destruction_id = data["destruction_id"]
        latitude = data["latitude"]
        longnitude = data["longnitude"]
        bag_data = data["bag_data"]
        lr_number = get_strip_lr_number(lr_number)
        table_headings = [["Bag UID", "Actual Weight", "New Weight", "Destruction Master", "Destruction Centre"]]
        print("destruction lr request")
        import json
        print(json.dumps(data))
    except Exception as e:
        print(e)
        return jsonify(status=500,message="Wrong Input")
    try:
        exist_pickup_obj = depopickup.query.filter_by(lr_number=lr_number).first()
        if exist_pickup_obj is not None:
            if exist_pickup_obj.status == "collected":
                return jsonify(status=500,message="LR number already collected!")
            if exist_pickup_obj.status == "submitted":
                return jsonify(status=500,message="LR number already submitted!")
        if exist_pickup_obj is None:
            return jsonify(status=500,message="LR number not exist!")
    except Exception as e:
        print(e)
        return jsonify(status=500,message="lr number exist check")
    try:
        depo_master_obj = userinfo.query.filter_by(id=destruction_master_id).first()
        depo_master_name = depo_master_obj.name
    except Exception as e:
        print(e)
        return jsonify(status=500,message="no destruction master found")
    try:
        depo_obj = destructionvendor.query.filter_by(id=destruction_id).first()
        depo_name = depo_obj.vendor_name
    except Exception as e:
        print(e)
        return jsonify(status=500,message="no destruction centre found")
    is_deviation = False
    if bag_data is not None and len(bag_data) !=0:
        for temp_bag in bag_data:
            if temp_bag["status"] == "incorrect":
                try:
                    submit_obj = destructioninventory(destruction_id=destruction_id,bag_id=temp_bag["bag_id"],status="received",latitude=latitude,
                                            longnitude=longnitude,created_at=datetime.datetime.now(),
                                            submitted_by=destruction_master_id)
                    deviated_data = temp_bag["deviated_data"]
                    deviated_bag_obj = deviateddestructionbag(bag_id=temp_bag["bag_id"],weight=deviated_data["weight"],
                                                remarks=deviated_data["remarks"], created_at=datetime.datetime.now()
                                                ,image_url=deviated_data["imageURL"])
                    db.session.add(submit_obj)
                    db.session.add(deviated_bag_obj)
                    bag_obj = bag.query.filter_by(id=temp_bag["bag_id"]).first()
                    bag_obj.status = "received"
                    table_headings.append([bag_obj.uid,bag_obj.weight, deviated_data["weight"], depo_master_name,depo_name])
                    if is_deviation == False:
                        is_deviation = True
                except Exception as e:
                    print(e)
                    db.session.rollback()
                    db.session.close()
                    return jsonify(status=500,message="error while saving deviated bags")
            else:
                try:
                    bag_obj = bag.query.filter_by(id=temp_bag["bag_id"]).first()
                    if temp_bag["bag_weight"] == bag_obj.weight:
                        submit_obj = destructioninventory(destruction_id=destruction_id,bag_id=temp_bag["bag_id"],status="received",latitude=latitude,
                                                longnitude=longnitude,created_at=datetime.datetime.now(),
                                                submitted_by=destruction_master_id)
                        db.session.add(submit_obj)
                        bag_obj.status = "received"
                    else:
                        return jsonify(status=500,message="Bag {0} weight Mismatch!".format(bag_obj.uid))
                except Exception as e:
                    print(e)
                    db.session.rollback()
                    db.session.close()
                    return jsonify(status=500,message="error while saving right weight bags")
        try:
            pickup_obj = depopickup.query.filter_by(lr_number=lr_number).first()
            pickup_obj.status = "collected"
            pickup_obj.deviated_weight = deviated_weight
            db.session.commit()
            temp_des_vendor = destructionvendor.query.filter_by(id=destruction_id).first()
            if temp_des_vendor is not None:
                return jsonify(status=200,message="{0}, Bags Submitted Successfully!".format(depo_master_name.capitalize()))
            return jsonify(status=200,message="{0}, Bags Submitted Successfully!".format(depo_master_name.capitalize()))
        except Exception as e:
            print(e)
            db.session.rollback()
            db.session.close()
            return jsonify(status=500,message="error while compeleting pickup!")
    else:
        return jsonify(status=500,message="no bag data to save")

# submit bag objects directly in depo with submit bag button


save_bag_obj = {

    "destruction_master_id" : "14",
    "destruction_id" : "1",
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
            pickup_obj = depopicktobag.query.filter_by(bag_id=temp_bag["bag_id"]).first()
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
    try:
        data = request.get_json(force=True)
        destruction_master_id = data["destruction_master_id"]
        destruction_id = data["destruction_id"]
        bag_data = data["bag_data"]
        latitude = data["latitude"]
        longnitude = data["longnitude"]
        print("destruction request")
        print(json.dumps(data))
    except Exception as e:
        print(e)
        print("error in query parameters!")
        
    table_headings = [["Bag UID", "Actual Weight", "New Weight", "Destruction Master", "Destruction Centre"]]
    seperate_bag_data = get_seperate_bag_data(bag_data)
    print(bag_data)
    print("below is seperated data")
    print(seperate_bag_data)
    is_deviation = False
    # truck_number = get_strip_truck_number(truck_number)
    try:
        depo_master_obj = userinfo.query.filter_by(id=destruction_master_id).first()
        destruction_master_name = depo_master_obj.name
    except Exception as e:
        print(e)
        return jsonify(status=500,message="No Destruction master found")
    try:
        depo_obj = destructionvendor.query.filter_by(id=destruction_id).first()
        destruction_name = depo_obj.vendor_name
    except Exception as e:
        print(e)
        return jsonify(status=500,message="No Destruction centre found")
    if len(seperate_bag_data.values()) != 0:
        for key, value in seperate_bag_data.items():
            # temp_truck_obj = depopickup.query.filter_by(id=key).first()
            # if temp_truck_obj.truck_number == truck_number:
            # temp_pickup_obj = depopicktobag.query.filter_by(pick_id=key).count()
            for temp_bag in value:
                if temp_bag["status"] == "incorrect":
                    try:
                        submit_obj = destructioninventory(destruction_id=destruction_id,bag_id=temp_bag["bag_id"],status="collected",latitude=latitude,
                                                longnitude=longnitude,created_at=datetime.datetime.now(),
                                                submitted_by=destruction_master_id)
                        deviated_data = temp_bag["deviated_data"]
                        deviated_bag_obj = deviateddestructionbag(bag_id=temp_bag["bag_id"],weight=deviated_data["weight"],
                                                    remarks=deviated_data["remarks"], created_at=datetime.datetime.now()
                                                    ,image_url=deviated_data["imageURL"])
                        db.session.add(submit_obj)
                        db.session.add(deviated_bag_obj)
                        bag_obj = bag.query.filter_by(id=temp_bag["bag_id"]).first()
                        bag_obj.status = "received"
                        new_weight = deviated_data["weight"]
                        actual_weight = bag_obj.weight
                        table_headings.append([bag_obj.uid,bag_obj.weight, deviated_data["weight"], destruction_master_name,destruction_name])
                        if is_deviation == False:
                            is_deviation = True
                    except Exception as e:
                        print(e)
                        db.session.rollback()
                        db.session.close()
                        return jsonify(status=500,message="error in saving deviated bags")
                    
                else:
                    try:
                        bag_obj = bag.query.filter_by(id=temp_bag["bag_id"]).first()
                        if temp_bag["bag_weight"] != bag_obj.weight:
                            db.session.rollback()
                            db.session.close()
                            return jsonify(status=500,message="no data to save")
                        submit_obj = destructioninventory(destruction_id=destruction_id,bag_id=temp_bag["bag_id"],status="collected",latitude=latitude,
                                                longnitude=longnitude,created_at=datetime.datetime.now(),
                                                submitted_by=destruction_master_id)
                        db.session.add(submit_obj)
                        bag_obj.status = "received"
                    except Exception as e:
                        print(e)
                        db.session.rollback()
                        db.session.close()
                        return jsonify(status=500,message="error in saving right bags")
                    
        
                try:
                    total_pickup_obj = depopicktobag.query.filter_by(pick_id=key).all()
                    if total_pickup_obj is not None:
                        total_pickup_bag = len(total_pickup_obj)
                        received_count = 0
                        for temp_bag in total_pickup_obj:
                            temp_bag_obj = bag.query.filter_by(id=temp_bag.bag_id).first()
                            if temp_bag_obj.status == "received":
                                received_count += 1
                        bag_difference = total_pickup_bag - received_count
                        if bag_difference == 0:
                            temp_pick_object = depopickup.query.filter_by(id=key).first()
                            temp_pick_object.status = "collected"
                except Exception as e:
                    print(e)
                    return jsonify(status=500,message="Error in Marking Pickup!")

                # temp_pick_object = depopickup.query.filter_by(id=key).first()
                # print(temp_pick_object.id, key)
                # temp_pick_object.status = "collected"
                try:
                    if is_deviation == True:
                        send_email(tabulate(table_headings, tablefmt='html'))
                except Exception as e:
                    print(e)
                    print("error in sending email")
            # else:
            #     return jsonify(status=500,message="truck number mismatch!")
        db.session.commit()
        des_vendor = destructionvendor.query.filter_by(id=destruction_id).first()
        return jsonify(status=200,message="Bags submitted at {0}".format(des_vendor.vendor_name))
    else:
        return jsonify(status=500,message="bag count missing") 


@blueprint.route('/change_psw',methods=['GET','POST'])
def change_psw():
    user_obj = userinfo.query.filter_by(id=29).first()
    user_password_bytes  = hash_pass("santosh")
    user_obj.password = "santosh"
    db.session.commit()



# delete data for destruction
@blueprint.route("/deletedes",methods=['GET', 'POST'])
def deletedes():
    des_obj = destructioninventory.query.delete()
    des_obj = deviateddestructionbag.query.delete()
    db.session.commit()
    return jsonify('data deleted')


# delete data for depot picker
@blueprint.route("/deletepicker",methods=['GET', 'POST'])
def deletepicker():
    des_obj = depopickup.query.delete()
    des_obj = depopicktobag.query.delete()
    des_obj = deviateddepopickbag.query.delete()
    db.session.commit()
    return jsonify('data deleted')



# delete data for depot
@blueprint.route("/deletedepot",methods=['GET', 'POST'])
def deletedepot():
    des_obj = depoinventory.query.delete()
    des_obj = deviateddepobag.query.delete()
    db.session.commit()
    return jsonify('data deleted')

# delete data for transport
@blueprint.route("/deletetrans",methods=['GET', 'POST'])
def deletetrans():
    des_obj = picktobag.query.delete()
    des_obj = pickup.query.delete()
    des_obj = deviatedbag.query.delete()
    db.session.commit()
    return jsonify('data deleted')


# delete data for audit
@blueprint.route("/deleteaudit",methods=['GET', 'POST'])
def deletetaudit():
    des_obj = bagtosku.query.delete()
    des_obj = auditsku.query.delete()
    
    # des_obj = sku.query.delete()
    des_obj = disttobag.query.delete()
    des_obj = audittobag.query.delete()
    des_obj = bag.query.delete()
    des_obj = audit.query.delete()
    db.session.commit()
    return jsonify('data deleted')