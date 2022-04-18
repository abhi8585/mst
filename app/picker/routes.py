from email import message

from itsdangerous import exc

from app import transporter
from app.picker import blueprint
from flask_restful import Resource, Api
from flask import jsonify, render_template, redirect, request, url_for
import json
from app.base.util import verify_pass
from app.models import audit, bag, sku, auditsku, bagtosku, audittobag, disttobag, pickup, picktobag, transtovendor, transportvendor, disttovendor, distvendor
from app.models import deviatedbag, userinfo

from app.models import depotopicker, depovendor, depopickup, depoinventory, depopicktobag, deviateddepopickbag, depoinventory
from app import db
import datetime
from flask_mail import Message
from tabulate import tabulate
from app import mail



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
        temp["depo_code"] = vendor.vendor_code
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

def send_email(html):

    try:
        msg = Message("Bag Marked deviated by Picker",
                  recipients=["sharma.abhi1114@gmail.com"])
        msg.html = html
        mail.send(msg)
        print("mail sent")
    except Exception as e:
        print(e)

def get_strip_truck_number(truck_number):
    new_truck_number = truck_number.replace(" ", "").lower()
    return new_truck_number    

def get_strip_lr_number(truck_number):
    new_lr_number = truck_number.replace(" ", "").lower()
    return new_lr_number


# helper functiont to delete created pickup in case if any error occur while saving bag data
def delete_pickup(pick_id):
    try:
        print("pickup id is {}".format(pick_id))
        temp_pick_bag = depopicktobag.query.filter_by(pick_id=pick_id).delete()
        temp_pickup = depopickup.query.filter_by(id=pick_id).delete()
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
                    if temp_bag.status == "dispatched":
                        temp_bag.status = "collected"
                        temp_bag.updated_at = datetime.datetime.now()
                temp_dist_bag = depoinventory.query.filter_by(bag_id=i).first()
                if temp_dist_bag is not None:
                    if temp_dist_bag.status == "dispatched":
                        temp_dist_bag.status = "collected"
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
                temp_pick_bag = deviateddepopickbag.query.filter_by(bag_id=i).delete()
                temp_bag = bag.query.filter_by(id=i).first()
                if temp_bag is not None:
                    if temp_bag.status == "dispatched":
                        temp_bag.status = "collected"
                        temp_bag.updated_at = datetime.datetime.now()
                temp_dist_bag = depoinventory.query.filter_by(bag_id=i).first()
                if temp_dist_bag is not None:
                    if temp_dist_bag.status == "dispatched":
                        temp_dist_bag.status = "collected"
                        temp_dist_bag.updated_at = datetime.datetime.now()
            db.session.commit()
            return dict(message=True)
        except Exception as e:
            print(e)
            print("while deleting an picktobag")
            return dict(message=False)
    else:
        return dict(message=True)

# create depo pickup object and map it to bag
@blueprint.route('/create_pickup',methods=["GET","POST"])
def create_pickup():
    import json
    try:
        data = request.get_json(force=True)
        picker_id = data["picker_id"]
        truck_number = data["truck_number"]
        lr_number = data["lr_number"]
        latitude = data["latitude"]
        longnitude = data["longnitude"]
        depo_id = data["depo_id"]
        bag_data = data["bag_data"]
        table_headings = [["Bag UID", "Actual Weight", "New Weight", "Depo Master", "Depo Name"]]
        pickup_number = depopickup.query.count() + 1
        asn_number = "ASN00MND00TNT{0}".format(pickup_number)
        is_deviation = False
        prev_right_bag_ids = []
        prev_wrong_bag_ids = []
        print("depo picker request")
        print(json.dumps(data))
    except Exception as e:
        print(e)
        print("error while getting parameters")
        return jsonify(status=500,message="Error while getting parameters!")
    # strip lr number
    lr_number = get_strip_lr_number(lr_number)
    # get the picker name for email
    try:
        depo_picker_obj = userinfo.query.filter_by(id=picker_id).first()
        depo_picker_name = depo_picker_obj.name
    except Exception as e:
        print(e)
        return jsonify(status=500,message="No depo picker found!")
    # get the depo name for emai
    try:
        depo_obj = depovendor.query.filter_by(id=depo_id).first()
        depo_name = depo_obj.vendor_name
    except Exception as e:
        print(e)
        return jsonify(status=500,message="No depo found!")
    try:
        temp_lr = depopickup.query.filter_by(lr_number=lr_number).first()
        if temp_lr is not None:
            return jsonify(status=500,message="LR number already exists!")
    except Exception as e:
        return jsonify(status=500,message="Wrong LR number!")
    try:
        pickup_obj = depopickup(picker_id=picker_id,truck_number=truck_number,latitude=latitude,longnitude=longnitude,
                            depo_id=depo_id,asn_number=asn_number,lr_number=lr_number,status="picked",created_at=datetime.datetime.now())
        db.session.add(pickup_obj)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        db.session.close()
        return jsonify(status=500, message="Cannot create pickup, Please check data again!")
    if len(bag_data) != 0:
        for bag_id in bag_data:
            if bag_id["deviated_data"] != "" and bag_id["status"] == "incorrect":
                try:
                    temp_bag_obj = bag.query.filter_by(id=bag_id["bag_id"]).first()
                    
                    # check if deviated bag exists or not
                    if temp_bag_obj is None:

                        # deleting pickup

                        try:
                            is_delete = delete_pickup(pickup_obj.id) 
                        except Exception as e:
                            print(e)
                            print("error while deleting pickup when bag is None")
                        try:
                            is_delete = delete_bagpick(prev_right_bag_ids)
                        except Exception as e:
                            print(e)
                            print("error while deleting right bags when bag is None")
                        
                        # deleting deviated bags
                        try:
                            is_delete = delete_deviated_bag(prev_wrong_bag_ids)
                        except Exception as e:
                            print(e)
                        
                        db.session.rollback()
                        db.session.close()
                        return jsonify(status=500,message="Bag {0} does not exist!".format(bag_id["bag_id"]))

                    # check if bag already marked deviated 

                    temp_deviated_bag = deviateddepopickbag.query.filter_by(bag_id=bag_id["bag_id"]).first()
                    if temp_deviated_bag is not None:
                        
                        # deleting pickup
                        try:
                            is_delete = delete_pickup(pickup_obj.id) 
                        except Exception as e:
                            print(e)
                            print("error while deleting pickup when bag is None")
                        
                        # deleting right bags
                        try:
                            is_delete = delete_bagpick(prev_right_bag_ids)
                        except Exception as e:
                            print(e)
                            print("error while deleting right bags when bag is None")
                        
                        # deleting deviated bags
                        try:
                            is_delete = delete_deviated_bag(prev_wrong_bag_ids)
                        except Exception as e:
                            print(e)
                        db.session.rollback()
                        db.session.close()
                        return jsonify(status=500,message="Bag {0} already marked as Deviated!".format(temp_bag_obj.uid))

                    # check if bag is already picked
                    if temp_bag_obj.status == "dispatched":
                        
                        # deleting pickup
                        try:
                            is_delete = delete_pickup(pickup_obj.id)
                        except Exception as e:
                            print(e)
                            print("error while deleting pickup when bag is dispatched!")
                       
                        # deleting right bags
                        try:
                            is_delete = delete_bagpick(prev_right_bag_ids)
                        except Exception as e:
                            print(e)
                            print("error while deleting right bags when bag is dispatched!")
                        
                        # deleting deviated bags
                        try:
                            is_delete = delete_deviated_bag(prev_wrong_bag_ids)
                        except Exception as e:
                            print(e)
                        db.session.rollback()
                        db.session.close()
                        return jsonify(status=500,message="Bag {0} already picked!".format(temp_bag_obj.uid))

                    # another check if bag is already picked
                    temp_pickup_depo = depopicktobag.query.filter_by(bag_id=temp_bag_obj.id).first()
                    if temp_pickup_depo is not None:
                        
                        # deleting pickup
                        try:
                            is_delete = delete_pickup(pickup_obj.id)
                        except Exception as e:
                            print(e)
                            print("error while deleting pickup when bag is already picked!")
                        
                        # deleting right bags
                        try:
                            is_delete = delete_bagpick(prev_right_bag_ids)
                        except Exception as e:
                            print(e)
                            print("error while deleting right bags when bag is already picked!")
                        
                        # deleting deviated bags
                        try:
                            is_delete = delete_deviated_bag(prev_wrong_bag_ids)
                        except Exception as e:
                            print(e)
                        db.session.rollback()
                        db.session.close()
                        return jsonify(status=500,message="Bag {0} already picked!".format(temp_bag_obj.uid))

                    # trying saving the deviated bags

                    try:
                        temp = bag_id["deviated_data"]
                        deviate_bag = deviateddepopickbag(bag_id=bag_id["bag_id"],weight=temp["weight"],
                                                remarks=temp["remarks"],created_at=datetime.datetime.now())
                        
                        # commenting to not map deviated bag to depo pickup
                        pick_bag_obj = depopicktobag(bag_id=bag_id["bag_id"],pick_id=pickup_obj.id,
                                            status=bag_id["status"],created_at=datetime.datetime.now())
                        db.session.add(pick_bag_obj)
                        db.session.add(deviate_bag)
                        
                        # no need to mark bag as dispatched beacuse its deviated bag
                        temp_bag_obj.status = "dispatched"
                        # no need to mark bag as dispatched beacuse its deviated bag
                        temp_dist_bag = depoinventory.query.filter_by(bag_id=bag_id["bag_id"]).first()
                        temp_dist_bag.status = "dispatched"
                        actual_weight = temp_bag_obj.weight
                        new_weight = temp["weight"]
                        table_headings.append([temp_bag_obj.uid,actual_weight, new_weight, depo_picker_name,depo_name])
                        prev_wrong_bag_ids.append(bag_id["bag_id"])
                        if is_deviation == False:
                            is_deviation = True
                    except Exception as e:
                        print(e)

                        # deleting pickup
                        try:
                            is_delete = delete_pickup(pickup_obj.id)
                        except Exception as e:
                            print(e)
                            # print("error while deleting pickup when bag is already picked!")
                        
                        # deleting right bags
                        try:
                            is_delete = delete_bagpick(prev_right_bag_ids)
                        except Exception as e:
                            print(e)
                        
                        # deleting deviated bags
                        try:
                            is_delete = delete_deviated_bag(prev_wrong_bag_ids)
                        except Exception as e:
                            print(e)
                            # print("error while deleting right bags when bag is already picked!")
                            return jsonify(status=500,message="Cannot save Deviated bags!".format(temp_bag_obj.uid))
                except Exception as e:
                    print(e)

                    # deleting pickup
                    try:
                        is_delete = delete_pickup(pickup_obj.id)
                    except Exception as e:
                        print(e)
                        print("error while deleting pickup")

                    # deleting right bags
                    try:
                        is_delete = delete_bagpick(prev_right_bag_ids)
                    except Exception as e:
                        print(e)
                    
                    # deleting deviated bags
                    try:
                        is_delete = delete_deviated_bag(prev_wrong_bag_ids)
                    except Exception as e:
                        print(e)
                            # print("error while deleting right bags when bag is already picked!")
                    db.session.rollback()
                    db.session.close()
                    return jsonify(status=500,message="Deviated bag data can not save")
            
            # saving the right bag
            
            else:
                # temp_bag = bag_id
                try:
                    temp_bag_obj = bag.query.filter_by(id=bag_id["bag_id"]).first()
                    # check if bag exists or not
                    if temp_bag_obj is None:
                        try:
                            is_delete = delete_pickup(pickup_obj.id) 
                        except Exception as e:
                            print(e)
                            print("error while deleting pickup when bag is None")
                        try:
                            is_delete = delete_bagpick(prev_right_bag_ids)
                        except Exception as e:
                            print(e)
                            print("error while deleting right bags when bag is None")
                        
                        # deleting deviated bags
                        try:
                            is_delete = delete_deviated_bag(prev_wrong_bag_ids)
                        except Exception as e:
                            print(e)
                        db.session.rollback()
                        db.session.close()
                        return jsonify(status=500,message="Bag {0} does not exist!".format(bag_id["bag_id"]))

                    # check if bag is already picked
                    if temp_bag_obj.status == "dispatched":
                        try:
                            is_delete = delete_pickup(pickup_obj.id)
                        except Exception as e:
                            print(e)
                            print("error while deleting pickup when bag is dispatched!")
                        # deleting right bags
                        try:
                            is_delete = delete_bagpick(prev_right_bag_ids)
                        except Exception as e:
                            print(e)
                            print("error while deleting right bags when bag is dispatched!")

                        # deleting deviated bags
                        try:
                            is_delete = delete_deviated_bag(prev_wrong_bag_ids)
                        except Exception as e:
                            print(e)

                        db.session.rollback()
                        db.session.close()
                        return jsonify(status=500,message="Bag {0} already picked!".format(temp_bag_obj.uid))

                    # another check if bag is already picked
                    temp_pickup_depo = depopicktobag.query.filter_by(bag_id=temp_bag_obj.id).first()
                    if temp_pickup_depo is not None:
                        try:
                            is_delete = delete_pickup(pickup_obj.id)
                        except Exception as e:
                            print(e)
                            print("error while deleting pickup when bag is already picked!")
                        try:
                            is_delete = delete_bagpick(prev_right_bag_ids)
                        except Exception as e:
                            print(e)
                            print("error while deleting right bags when bag is already picked!")

                        # deleting deviated bags
                        try:
                            is_delete = delete_deviated_bag(prev_wrong_bag_ids)
                        except Exception as e:
                            print(e)
                        db.session.rollback()
                        db.session.close()
                        return jsonify(status=500,message="Bag {0} already picked!".format(temp_bag_obj.uid))

                    # check if right bag data weights match 
                    if temp_bag_obj.weight == bag_id["bag_weight"]:
                        pick_bag_obj = depopicktobag(bag_id=bag_id["bag_id"],pick_id=pickup_obj.id,
                                        status=bag_id["status"],created_at=datetime.datetime.now())
                        db.session.add(pick_bag_obj)
                        temp_bag_obj.status = "dispatched"
                        temp_dist_bag = depoinventory.query.filter_by(bag_id=bag_id["bag_id"]).first()
                        # raise ValueError(temp_dist_bag.status)
                        temp_dist_bag.status = "dispatched"
                        prev_right_bag_ids.append(bag_id["bag_id"])
                    else:
                        # deleting pickup
                        try:
                            is_delete = delete_pickup(pickup_obj.id)
                        except Exception as e:
                            print(e)
                            print("error while deleting pickup when right bag weight not matching!")
                        # deleting right bags
                        try:
                            is_delete = delete_bagpick(prev_right_bag_ids)
                        except Exception as e:
                            print(e)
                            print("error while deleting right bags when bag data mismatch!")
                        
                        # deleting deviated bags
                        try:
                            is_delete = delete_deviated_bag(prev_wrong_bag_ids)
                        except Exception as e:
                            print(e)

                        db.session.rollback()
                        db.session.close()
                        return jsonify(status=500,message="Bag {0} weight not match!".format(temp_bag_obj.uid))
                except Exception as e:
                    print(e)
                    db.session.rollback()
                    db.session.close()
                    return jsonify(status=500,message="Cannot create pickup, Please check Non-deviated bags again!")
        try:
            if is_deviation == True:
                # pass
                send_email(tabulate(table_headings, tablefmt='html'))
        except Exception as e:
            print(e)
            print("error in sending email!")
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            print("error while committing bag to pickup!")
            # deleting pickup
            try:
                is_delete = delete_pickup(pickup_obj.id)
            except Exception as e:
                print(e)
                print("error while deleting pickup when commiting bag to pickup")
            # deleting right bags
            try:
                is_delete = delete_bagpick(prev_right_bag_ids)
            except Exception as e:
                print(e)
                print("error while deleting right bags when commiting the bag to picks")
            # deleting deviated bags
            try:
                is_delete = delete_deviated_bag(prev_wrong_bag_ids)
            except Exception as e:
                print(e)
                
            return jsonify(status=500,message="Cannot commit pickup data, Please reach out to Manager!")
        return jsonify(status=200,pickup_number = asn_number,message="{0}, Bags picked successfully!".format(depo_picker_name.capitalize()))
    else:
        db.session.rollback()
        db.session.close()
        # deleting pickup
        try:
            is_delete = delete_pickup(pickup_obj.id)
        except Exception as e:
            print(e)
            print("error while deleting pickup when no bag data is available!")
        # deleting right bags
        try:
            is_delete = delete_bagpick(prev_right_bag_ids)
        except Exception as e:
            print(e)
            print("error while deleting right bags when no bag to pick")
        return jsonify(status=500,message="No bags available to Pickup!")


@blueprint.route('/get_depo_pickup', methods=['POST'])
def get_depo_pickup():
    data = request.get_json(force=True)
    picker_id = data["picker_id"]
    pickup_obj = depopickup.query.filter_by(picker_id=picker_id, status="picked").all()
    if pickup_obj is None:
        return jsonify(status=500,message="no pickups by you!")
    pickup_data = []
    if len(pickup_obj) > 0:
        for pick in pickup_obj:
            temp = {}
            bag_count = depopicktobag.query.filter_by(pick_id=pick.id).count()
            if bag_count > 0 :
                temp["total_bag"] = bag_count
                temp["pickup_number"] = pick.asn_number
                temp["lr_number"] = pick.lr_number
                temp["date"] = pick.created_at.strftime("%Y-%m-%d")
                pickup_data.append(temp)
    else:
        return jsonify(status=500,message="no pickups")
    if len(pickup_data) != 0:
        return jsonify(status=200,pickup_data=pickup_data)
    else:
        return jsonify(status=500,message="no pickup")