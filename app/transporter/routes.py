from email import message
from operator import sub
from shutil import ExecError


from itsdangerous import exc
from app import transporter
from app.transporter import blueprint
from flask_restful import Resource, Api
from flask import jsonify, render_template, redirect, request, url_for
import json
from app.base.util import verify_pass
from app.models import audit, bag, depoinventory, depopickup, role,sku, auditsku, bagtosku, audittobag, disttobag, pickup, picktobag, transtovendor, transportvendor, disttovendor, distvendor, userinfo, usertorole
from app.models import deviatedbag, depopicktobag, destructioninventory
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


@blueprint.route('/get_bag_data',methods=['POST'])
def get_bag_data():
    try:
        data = request.get_json(force=True)
        bag_uid = data["bag_uid"]
        user_id = data["user_id"]
        distributor_id = data["distributor_id"]
        depo_id = data["depo_id"]
    except Exception as e:
        return jsonify(status=500,message="Error in query parameters")
    # find user role
    temp_role_obj = usertorole.query.filter_by(user_id=user_id).first()
    if temp_role_obj is not None:
        temp_role_name = role.query.filter_by(id=temp_role_obj.role_id).first()

    # for the transporter role

        if str(temp_role_name.name) == "transporter":
            # now check if transporter is eligble or not to pick the bag
            bag_data = bag.query.filter_by(uid=bag_uid).first()
            
            # first check if the bag really mapped to the select distributor.
            
            if bag_data is not None:
                dist_bag_obj = disttobag.query.filter_by(bag_id=bag_data.id).first()
                if dist_bag_obj is not None:
                    if str(dist_bag_obj.dist_id) != distributor_id:
                        return jsonify(status=500,message="This bag is not available on the selected distributor!".format(bag_uid))
                if bag_data.status != "audited":
                    return jsonify(status=500,message="{0} is already picked!".format(bag_uid))
                temp_bag_pick = picktobag.query.filter_by(bag_id=bag_data.id).first()
                if temp_bag_pick is not None:
                    return jsonify(status=500,bag_data=[],message="{0} is already picked!".format(bag_uid))
                try:
                    # commenting because now we dont show the sku on UI
                    # bag_sku = bagtosku.query.filter_by(bag_id = bag_data.id).all()
                    temp = dict(bag_weight=bag_data.weight,bag_id=bag_data.id,bag_status = bag_data.status,sku_data=[])
                    return jsonify(status=200,bag_data=temp,message="Scanning right Bag!")
                except Exception as e:
                    print(e)
                    return jsonify(status=500,message="Invalid Bag!")
            else:
                return jsonify(status=500,message="QR code is Invalid!")

        # for depo master

        if str(temp_role_name.name) == "depo master":
            # check if bag exists
            bag_data = bag.query.filter_by(uid=bag_uid).first()
            if bag_data is not None:
                temp_depo_obj = depoinventory.query.filter_by(bag_id = bag_data.id).first()
                if temp_depo_obj is not None:
                    return jsonify(status=500,message="{0} is already submitted at Warehouse!".format(bag_uid))
                if str(bag_data.status) != "picked":
                    return jsonify(status=500,message="Cannot pickup bag it's in {0} state!".format(str(bag_data.status.capitalize())))
                if str(bag_data.status) == "collected":
                    print("from the collection")
                    return jsonify(status=500,message="{0} is already submitted at Warehouse!".format(bag_uid))
                
                # if pass all the checks make the data structure
                try:
                    temp = dict(bag_weight=bag_data.weight,bag_id=bag_data.id,bag_status = bag_data.status,sku_data=[])
                    return jsonify(status=200,bag_data=temp,message="Scanning right Bag!")
                except Exception as e:
                    print(e)
                    return jsonify(status=500,message="Invalid Bag!")
            else:
                return jsonify(status=500,message="QR code is Invalid!")
        
        # for the picker role

        if str(temp_role_name.name) == "depo picker":
            # now check if transporter is eligble or not to pick the bag
            bag_data = bag.query.filter_by(uid=bag_uid).first()
            
            # first check if the bag really mapped to the select distributor.
            
            if bag_data is not None:
                dist_bag_obj = depoinventory.query.filter_by(bag_id=bag_data.id).first()
                if dist_bag_obj is not None:
                    if str(dist_bag_obj.depo_id) != depo_id:
                        return jsonify(status=500,message="This bag is not available on the selected WareHouse!".format(bag_uid))
                
                temp_bag_pick = depopicktobag.query.filter_by(bag_id=bag_data.id).first()
                if temp_bag_pick is not None:
                    return jsonify(status=500,bag_data=[],message="{0} is already picked!".format(bag_uid))
                
                if str(bag_data.status) != "collected":
                    return jsonify(status=500,message="Cannot pickup bag it's in {0} state!".format(str(bag_data.status.capitalize())))
                
                try:
                    # commenting because now we dont show the sku on UI
                    # bag_sku = bagtosku.query.filter_by(bag_id = bag_data.id).all()
                    temp = dict(bag_weight=bag_data.weight,bag_id=bag_data.id,bag_status = bag_data.status,sku_data=[])
                    return jsonify(status=200,bag_data=temp,message="Scanning right Bag!")
                except Exception as e:
                    print(e)
                    return jsonify(status=500,message="Invalid Bag!")
            else:
                return jsonify(status=500,message="QR code is Invalid!")


        # for destruction master

        if str(temp_role_name.name) == "destruction master":
            # check if bag exists
            bag_data = bag.query.filter_by(uid=bag_uid).first()
            if bag_data is not None:
                temp_depo_obj = destructioninventory.query.filter_by(bag_id = bag_data.id).first()
                if temp_depo_obj is not None:
                    return jsonify(status=500,message="{0} is already submitted at Destruction Centre!".format(bag_uid))
                if str(bag_data.status) != "dispatched":
                    if str(bag_data.status) == "collected":
                        return jsonify(status=500,message="Cannot receive bag it's in Warehouse only!".format(str(bag_data.status)))
                if str(bag_data.status) == "received":
                    print("from the collection")
                    return jsonify(status=500,message="{0} is already submitted at Destruction Centre!".format(bag_uid))

                # if pass all the checks make the data structure
                try:
                    temp = dict(bag_weight=bag_data.weight,bag_id=bag_data.id,bag_status = bag_data.status,sku_data=[])
                    return jsonify(status=200,bag_data=temp,message="Scanning right Bag!")
                except Exception as e:
                    print(e)
                    return jsonify(status=500,message="Invalid Bag!")
            else:
                return jsonify(status=500,message="QR code is Invalid!")
    else:
        return jsonify(status=500, message="Please scan again!")

    # if bag_data is not None:
    #     bag_sku = bagtosku.query.filter_by(bag_id = bag_data.id).all()
    #     temp = dict(bag_weight=bag_data.weight,bag_id=bag_data.id,bag_status = bag_data.status,sku_data=[])
    
    #     for audit_sku in bag_sku:
    #         audit_sku_id = auditsku.query.filter_by(id=audit_sku.sku_id).first()
    #         sku_obj = sku.query.filter_by(id=audit_sku_id.sku_id).first()
    #         if sku_obj is not None:
    #             temp_sku = dict(audit_sku_id=audit_sku_id.id,sku_id=sku_obj.id,sku_weight=audit_sku_id.weight
    #                 ,sku_asn_code=audit_sku_id.asn_code,name=sku_obj.name,description=sku_obj.description)
    #             temp["sku_data"].append(temp_sku)
    #     return jsonify(status=200,bag_data=temp)
    # else:
    #     return jsonify(status=500,bag_data=[])




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
                  recipients=["sharma.abhi1114@gmail.com","romil.singh@qodenext.com"])
    # msg.recipients = [""]
    # msg.add_recipient("sharma.abhi1114@gmail.com")
    msg.html = html
    mail.send(msg)
    print("mail sent")

def get_strip_truck_number(truck_number):
    new_truck_number = truck_number.replace(" ", "").lower()
    return new_truck_number    

def get_strip_lr_number(lr_number):
    new_lr_number = lr_number.replace(" ", "").lower()
    return new_lr_number    


# helper functiont to delete created pickup in case if any error occur while saving bag data
def delete_pickup(pick_id):
    try:
        temp_pick_bag = picktobag.query.filter_by(pick_id=pick_id).delete()
        temp_pickup = pickup.query.filter_by(id=pick_id).delete()
        db.session.expunge_all()
        db.session.commit()
        return dict(message=True)
    except Exception as e:
        print(e)
        print("while deleting an pickup from the function")
        return dict(message=False)


# helper functiont to delete created bag in case if any error occur while saving right bag data
def delete_bagpick(bag_ids):
    if len(bag_ids) > 0:
        try:
            db.session.expunge_all()
            for i in bag_ids:
                print("bag id is {0}".format(i))
                temp_pick_bag = picktobag.query.filter_by(bag_id=i).delete()
                temp_bag = bag.query.filter_by(id=i).first()
                if temp_bag is not None:
                    if temp_bag.status == "picked":
                        temp_bag.status = "audited"
                        temp_bag.updated_at = datetime.datetime.now()
                temp_dist_bag = disttobag.query.filter_by(bag_id=i).first()
                if temp_dist_bag is not None:
                    if temp_dist_bag.status == "picked":
                        temp_dist_bag.status = "audited"
                        temp_dist_bag.updated_at = datetime.datetime.now()
            db.session.commit()
            return dict(message=True)
        except Exception as e:
            print(e)
            print("while deleting an picktobag")
            return dict(message=False)
    else:
        return dict(message=True)


# helper functiont to delete created deviated bag in case if any error occur while saving right/deviated bag data
def delete_deviated_bag(bag_ids):
    if len(bag_ids) > 0:
        try:
            db.session.expunge_all()
            for i in bag_ids:
                print("deviated bag id is {0}".format(i))
                temp_pick_bag = deviatedbag.query.filter_by(bag_id=i).delete()
            db.session.commit()
            return dict(message=True)
        except Exception as e:
            print(e)
            print("while deleting an picktobag")
            return dict(message=False)
    else:
        return dict(message=True)


def get_seperate_bag_data(bag_list):
    temp_data = bag_list
    audit_data = {}
    try:
        for temp_bag in temp_data:
            audit_obj = audittobag.query.filter_by(bag_id=temp_bag).first()
            if audit_obj is None:
                pass
            if audit_obj is not None:
                if audit_obj.audit_id not in audit_data.keys():
                    audit_data[audit_obj.audit_id] = [temp_bag]
                else:
                    audit_data[audit_obj.audit_id].append(temp_bag)
        return audit_data
    except Exception as e:
        print(e)
        return audit_data


# create pickup object and map it to bag
@blueprint.route('/create_pickup',methods=["GET","POST"])
def create_pickup():
    import json
    import string
    import random
    try:
        try:
            data = request.get_json(force=True)
            print("below is the pickup request for transport")
            print(json.dumps(data))
            if data is None:
                return jsonify(status=200,message="no pickup data to save!")
        except Exception as e:
            print(e)
            print("error while getting data")
            return jsonify(status=500,message="error while getting data")
        transporter_id = data["transporter_id"]
        truck_number = data["truck_number"]
        try:
            lr_number = data["lr_number"]
            lr_number = get_strip_lr_number(lr_number)
            if lr_number == "":
                return jsonify(status=200,message="LR number can't be empty!")
        except Exception as e:
            print(e)
            print("error while getting lr number")
            return jsonify(status=500,message="error while getting lr number!")
        latitude = data["latitude"]
        longnitude = data["longnitude"]
        dist_id = data["dist_id"]
        bag_data = data["bag_data"]
        table_headings = [["Bag UID", "Actual Weight", "New Weight", "Transporter", "Distributor"]]
        is_deviation = False
        truck_number = get_strip_truck_number(truck_number)
        prev_right_bag_ids = []
        prev_wrong_bag_ids = []
        pickup_id = ""
    except Exception as e:
        print(e)
        return jsonify(status=500,message="something wrong query parameters!")
    try:
        trans_obj = userinfo.query.filter_by(id=transporter_id).first()
        transporter_name = trans_obj.name
    except Exception as e:
        print(e)
        return jsonify(status=500, message="no transporter found!")
   

    try:
        dist_obj = distvendor.query.filter_by(id=dist_id).first()
        dist_name = dist_obj.vendor_name
    except Exception as e:
        print(e)
        return jsonify(status=500, message="no distributor found!")
    try:
        temp_lr_number = pickup.query.filter_by(lr_number=lr_number).first()
        if temp_lr_number is not None:
            return jsonify(status=500,message="LR number already exists!")
    except Exception as e:
        print(e)
        return jsonify(status=500,message="Wrong LR number!")

    try:
        pickup_number = pickup.query.count() + 1
        pickup_number = "PCK00MND00TNT{0}".format(pickup_number)
    except Exception as e:
        print(e)
        print("while creating pickup number")
        return jsonify(status=500,message="error while creating pickup number")
    try:
        pickup_obj = pickup(transporter_id=transporter_id,truck_number=truck_number,lr_number=lr_number,latitude=latitude,longnitude=longnitude,
                            dist_id=dist_id,pickup_number=pickup_number,status="picked",created_at=datetime.datetime.now())
        db.session.add(pickup_obj)
        db.session.commit()
        pickup_id = pickup_obj.id
    except Exception as e:
        print(e)
        print("Error while creating pickup")
        db.session.expunge_all()
        db.session.rollback()
        db.session.close()
        return jsonify(status=500,message="can not create pickup!")
    if len(bag_data) != 0:
        for bag_id in bag_data:
            # saving deviated weight bag
            if bag_id["deviated_data"] != "" and bag_id["status"] == "incorrect": 
                
                temp_bag_obj = bag.query.filter_by(id=bag_id["bag_id"]).first()
                # check if bag already marked as deviated
                try:
                    temp_dev_bag = deviatedbag.query.filter_by(bag_id=bag_id["bag_id"]).first()
                    if temp_dev_bag is not None:
                        # delete deviated bag mapping object
                        try:
                            is_delete = delete_deviated_bag(prev_wrong_bag_ids)
                            
                        except Exception as e:
                            print(e)
                            print("error while deleting deviated bag")
                        # delete bag mapping object
                        try:
                            is_delete = delete_bagpick(prev_right_bag_ids)
                        except Exception as e:
                            print(e)
                            print("error while deleting bag to pick")
                        # delete pickup object
                        try:
                            is_delete = delete_pickup(pickup_obj.id)
                            
                        except Exception as e:
                            print(e)
                            print("error while deleting pickup")
                        return jsonify(status=500,message="bag {0} already marked deviated!".format(temp_bag_obj.uid))
                except Exception as e:
                    print(e)
                    print("error while checking existing deviated bag")
                    return jsonify(status=500,message="error while checking existing deviated bag")
                try:
                    # check if bags exist
                    if temp_bag_obj == None:
                        # delete deviated bag mapping object
                        try:
                            is_delete = delete_deviated_bag(prev_wrong_bag_ids)
                        except Exception as e:
                            print(e)
                            print("error while deleting deviated bag")
                        # delete bag mapping object
                        try:
                            is_delete = delete_bagpick(prev_right_bag_ids)
                            
                        except Exception as e:
                            print(e)
                            print("error while deleting bag to pick")
                        # delete pickup object
                        try:
                            is_delete = delete_pickup(pickup_obj.id)
                            
                        except Exception as e:
                            print(e)
                            print("error while deleting pickup")
                        return jsonify(status=500,message="bag {0} does not exist".format(bag_id["bag_id"]))
                    # check if bag already picked
                    if temp_bag_obj.status == "picked":
                        # delete deviated bag mapping object
                        try:
                            is_delete = delete_deviated_bag(prev_wrong_bag_ids)
                            
                        except Exception as e:
                            print(e)
                            print("error while deleting deviated bag")
                        # delete bag mapping object
                        try:
                            is_delete = delete_bagpick(prev_right_bag_ids)
                            
                        except Exception as e:
                            print(e)
                            print("error while deleting bag to pick")
                        # delete pickup object
                        try:
                            is_delete = delete_pickup(pickup_obj.id)
                            
                        except Exception as e:
                            print(e)
                            print("error while deleting pickup")
                        return jsonify(status=500,message="Bag {0} already".format(temp_bag_obj.uid))
                    # another check if bag is already picked
                    temp_pickup= picktobag.query.filter_by(bag_id=temp_bag_obj.id).first()
                    if temp_pickup is not None:
                        # delete deviated bag mapping object
                        try:
                            is_delete = delete_deviated_bag(prev_wrong_bag_ids)
                        except Exception as e:
                            print(e)
                            print("error while deleting deviated bag")
                        # delete bag mapping object
                        try:
                            is_delete = delete_bagpick(prev_right_bag_ids)
                        except Exception as e:
                            print(e)
                            print("error while deleting bag to pick")
                        # delete pickup object
                        try:
                            is_delete = delete_pickup(pickup_obj.id)
                        except Exception as e:
                            print(e)
                            print("error while deleting pickup")
                        return jsonify(status=500,message="Bag {0} already picked".format(temp_bag_obj.uid))
                except Exception as e:
                    print(e)
                    print("Error while checking deviated bag status")
                    # delete deviated bag mapping object
                    try:
                        is_delete = delete_deviated_bag(prev_wrong_bag_ids)
                        
                    except Exception as e:
                        print(e)
                        print("error while deleting deviated bag")
                    # delete bag mapping object
                    try:
                        is_delete = delete_bagpick(prev_right_bag_ids)
                        
                    except Exception as e:
                        print(e)
                        print("error while deleting bag to pick")
                    try:
                        is_delete = delete_pickup(pickup_obj.id)
                        
                    except Exception as e:
                        print(e)
                        print("error while deleting pickup")
                    return jsonify(status=500,message="Error in deviated bag")
                
                # bag data save
                try:
                    temp = bag_id["deviated_data"]
                    deviate_bag = deviatedbag(bag_id=bag_id["bag_id"],weight=temp["weight"],
                                        remarks=temp["remarks"],created_at=datetime.datetime.now(),pick_id=pickup_obj.id)
                # pick_bag_obj = picktobag(bag_id=bag_id["bag_id"],pick_id=pickup_obj.id,
                #                     status=bag_id["status"],created_at=datetime.datetime.now())
                # db.session.add(pick_bag_obj)
                    db.session.add(deviate_bag)
                    prev_wrong_bag_ids.append(bag_id["bag_id"])
                    # temp_bag_obj = bag.query.filter_by(id=bag_id["bag_id"]).first() already selected data above
                # temp_bag_obj.status = "picked"
                    # temp_dist_bag = disttobag.query.filter_by(bag_id=bag_id["bag_id"]).first()
                # temp_dist_bag.status = "picked"
                    actual_weight = temp_bag_obj.weight
                    new_weight = bag_id["deviated_data"]["weight"]
                    table_headings.append([temp_bag_obj.uid,actual_weight,new_weight,transporter_name,dist_name])
                    if is_deviation == False:
                        is_deviation = True

                except Exception as e:
                    print(e)
                    print("Error while saving deviated bag")
                    db.session.rollback()
                    db.session.close()
                    # delete deviated bag mapping object
                    try:
                        is_delete = delete_deviated_bag(prev_wrong_bag_ids)
                        
                    except Exception as e:
                        print(e)
                        print("error while deleting deviated bag")
                    # delete bag mapping object
                    try:
                        is_delete = delete_bagpick(prev_right_bag_ids)
                        
                    except Exception as e:
                        print(e)
                        print("error while deleting bag to pick")
                    # delete pickup object
                    try:
                        is_delete = delete_pickup(pickup_obj.id)
                        
                    except Exception as e:
                        print(e)
                        print("error while deleting pickup")
                    return jsonify(status=500,message="error in saving deviated bag")
            
            
            # saving right weight bags   
            else:
                temp_bag_obj = bag.query.filter_by(id=bag_id["bag_id"]).first()
                try:
                    # check if bag exist or not
                    if temp_bag_obj == None:
                        # delete deviated bag mapping object
                        try:
                            is_delete = delete_deviated_bag(prev_wrong_bag_ids)
                            
                        except Exception as e:
                            print(e)
                            print("error while deleting bag to pick")
                        # delete previous bag mappings
                        try:
                            is_delete = delete_bagpick(prev_right_bag_ids)
                            
                        except Exception as e:
                            print(e)
                            print("error while deleting bag to pick")
                        # delete pickup object
                        try:
                            db.session.expunge_all()
                            is_delete = delete_pickup(pickup_id)
                            
                        except Exception as e:
                            print(e)
                            print("error while deleting pickup")
                        return jsonify(status=500,message="bag {0} does not exist".format(bag_id["bag_id"]))
                # check if bag is already picked
                    if temp_bag_obj.status == "picked":
                        # delete deviated bag mapping object
                        try:
                            is_delete = delete_deviated_bag(prev_wrong_bag_ids)
                            
                        except Exception as e:
                            print(e)
                            print("error while deleting bag to pick")
                        # delete previous bag mappings
                        try:
                            is_delete = delete_bagpick(prev_right_bag_ids)
                            
                        except Exception as e:
                            print(e)
                            print("error while deleting pickup")
                        # delete pickup object
                        try:
                            is_delete = delete_pickup(pickup_obj.id)
                        except Exception as e:
                            print(e)
                            print("error while deleting pickup")
                        return jsonify(status=500,message="bag {0} already picked before".format(temp_bag_obj.uid))
                # another check if bag is already picked
                    temp_pickup= picktobag.query.filter_by(bag_id=temp_bag_obj.id).first()
                    if temp_pickup is not None:
                        # delete deviated bag mapping object
                        try:
                            is_delete = delete_deviated_bag(prev_wrong_bag_ids)
                        except Exception as e:
                            print(e)
                            print("error while deleting deviated bag")
                        # delete previous bag mappings
                        try:
                            is_delete = delete_bagpick(prev_right_bag_ids)                    
                        except Exception as e:
                            print(e)
                            print("error while deleting right bags")
                        
                        # delete pickup object
                        try:
                            is_delete = delete_pickup(pickup_obj.id)
                            
                        except Exception as e:
                            print(e)
                            print("error while deleting pickup")
                        return jsonify(status=500,message="bag {0} already picked".format(temp_bag_obj.uid))
                except Exception as e:
                    print(e)
                    print("Error while checking right bag status")
                    # delete deviated bag mapping object
                    try:
                        is_delete = delete_deviated_bag(prev_wrong_bag_ids)
                        
                    except Exception as e:
                        print(e)
                        print("error while deleting deviated bag")
                    # delete previous bag mappings
                    try:
                        is_delete = delete_bagpick(prev_right_bag_ids)
                        
                    except Exception as e:
                        print(e)
                        print("error while deleting pickup")
                    # delete pickup object
                    try:
                        is_delete = delete_pickup(pickup_obj.id)
                    except Exception as e:
                        print(e)
                        print("error while deleting pickup")
                    return jsonify(status=500,message="error in right bag checks")
                
                # saving right bag data
                try:
                    if temp_bag_obj.weight == bag_id["bag_weight"]:
                        pick_bag_obj = picktobag(bag_id=bag_id["bag_id"],pick_id=pickup_obj.id,
                                        status=bag_id["status"],created_at=datetime.datetime.now())
                        db.session.add(pick_bag_obj)
                        temp_bag_obj.status = "picked"
                        temp_dist_bag = disttobag.query.filter_by(bag_id=bag_id["bag_id"]).first()
                        temp_dist_bag.status = "picked"
                        prev_right_bag_ids.append(bag_id["bag_id"])
                    else:
                        db.session.expunge_all()
                        db.session.rollback()
                        db.session.close()
                        # delete deviated bag mapping object
                        try:
                            is_delete = delete_deviated_bag(prev_wrong_bag_ids)
                      
                        except Exception as e:
                            print(e)
                            print("error while deleting deviated bag")
                        # delete previous bag mappings
                        try:
                            is_delete = delete_bagpick(prev_right_bag_ids)
                            
                        except Exception as e:
                            print(e)
                            print("error while deleting pickup")
                        # delete pickup object
                        try:
                            is_delete = delete_pickup(pickup_obj.id)
                            
                        except Exception as e:
                            print(e)
                            print("error while deleting pickup")
                        return jsonify(status=500,message="bag {0} weight mismatch".format(temp_bag_obj.uid))
                except Exception as e:
                    print(e)
                    print("error while saving right bag")
                    # delete deviated bag mapping object
                    try:
                        is_delete = delete_deviated_bag(prev_wrong_bag_ids)
                        
                    except Exception as e:
                        print(e)
                        print("error while deleting deviated bag")
                    # delete previous bag mappings
                    try:
                        is_delete = delete_bagpick(prev_right_bag_ids)
                    except Exception as e:
                        print(e)
                        print("error while deleting pickup")
                    # delete pickup object
                    try:
                        is_delete = delete_pickup(pickup_obj.id)
                    except Exception as e:
                        print(e)
                        print("error while deleting pickup")
                    return jsonify(status=500,message="error while saving right bag")   
        # commit the bag data pickup data
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            print("error while commiting!")
            # delete deviated bag mapping object
            try:
                is_delete = delete_deviated_bag(prev_wrong_bag_ids)
                
            except Exception as e:
                print(e)
                print("error while deleting deviated bag")
            # delete previous bag mappings
            try:
                is_delete = delete_bagpick(prev_right_bag_ids)
                
            except Exception as e:
                print(e)
                print("error while deleting pickup")
            # delete pickup object
            try:
                is_delete = delete_pickup(pickup_obj.id)
                
            except Exception as e:
                print(e)
                print("error while deleting pickup")
            return jsonify(status=500,message="error while commiting!")
        # send email
        try:
            if is_deviation:
                send_email(tabulate(table_headings, tablefmt='html'))
                print("mail sent")
        except Exception as e:
            print(e)
            print("error in email")
        temp_user = userinfo.query.filter_by(id=transporter_id).first()
        return jsonify(status=200,pickup_number = pickup_number,message="Congratulations {0}, Bags picked up successfully!".format(temp_user.name.capitalize()))
    else:
        db.session.expunge_all()
        db.session.rollback()
        db.session.close()
        # delete deviated bag mapping objectf
        try:
            is_delete = delete_deviated_bag(prev_wrong_bag_ids)
            
        except Exception as e:
            print(e)
            print("error while deleting deviated bag")
        # delete previous bag mappings
        try:
            is_delete = delete_bagpick(prev_right_bag_ids)
            
        except Exception as e:
            print(e)
            print("error while deleting pickup")
        # delete pickup object
        try:
            is_delete = delete_pickup(pickup_obj.id)
        except Exception as e:
            print(e)
            print("error while deleting pickup")
        return jsonify(status=500,message="no bag data to store!")




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
        temp["distributor_code"] = vendor.vendor_code
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
            total_bag_count = 0
            temp = {}
            bags_obj = picktobag.query.filter_by(pick_id=pick.id).all()
            for temp_bag in bags_obj:
                bag_obj = bag.query.filter_by(id=temp_bag.bag_id).first()
                if bag_obj.status == "picked":
                    total_bag_count += 1
            dist_name = distvendor.query.filter_by(id=pick.dist_id).first()
            if total_bag_count > 0:
                temp["total_bag"] = total_bag_count
                temp["pickup_number"] = pick.pickup_number
                temp["date"] = pick.created_at.strftime("%Y-%m-%d")
                temp["lr_number"] = pick.lr_number
                temp["dist_name"] = dist_name.vendor_name
                pickup_data.append(temp)
    else:
        return jsonify(status=500,message="Sadly no Pickup for you!")
    if len(pickup_data) != 0:
        return jsonify(status=200,pickup_data=pickup_data)
    else:
        return jsonify(status=500,message="not able to get pickup data")

@blueprint.route('/delete',methods=["GET","POST"])
def delete():
    audit.query.delete()
    db.session.commit()
    return "data deleted"


@blueprint.route('/create_pickup_test', methods=['GET', 'POST'])
def create_pickup_test():
    data = request.get_json(force=True)
    bag_uid = data["bag_uid"]
    test_logs = []

    # start testing

    temp_bag = bag.query.filter_by(uid=bag_uid).all()
    if len(temp_bag) == 1:
        
        # GET BAG status
        test_logs.append("bag status is {0}".format(temp_bag[0].status))
        test_logs.append("bag weight is {0}".format(temp_bag[0].weight))
        temp_pickup = picktobag.query.filter_by(bag_id=temp_bag[0].id).all()
       
        if len(temp_pickup) == 1:
            temp_pickup = pickup.query.filter_by(id=temp_pickup[0].pick_id)
            test_logs.append("bag pickup id is {0}".format(temp_pickup[0].id))
            test_logs.append("bag lr number  is {0}".format(temp_pickup[0].lr_number))
            test_logs.append("bag truck number  is {0}".format(temp_pickup[0].truck_number))
        elif len(temp_pickup) == 0:
            test_logs.append("bag was marked deviated")

        
        # getting distributor status of bag

        temp_dist = disttobag.query.filter_by(bag_id=temp_bag[0].id).all()
        if len(temp_dist) == 1:
            test_logs.append("bag status at distributor is {0}".format(temp_dist[0].status))
            dist_name = distvendor.query.filter_by(id=temp_dist[0].dist_id).first()
            test_logs.append("bag picked from distributor {0}".format(dist_name.vendor_name))
    return jsonify(test_logs)


