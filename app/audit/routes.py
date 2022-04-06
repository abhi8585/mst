from email import message

from itsdangerous import exc
from app.audit import blueprint
from flask_restful import Resource, Api
from flask import jsonify, render_template, redirect, request, url_for
import json
from app.base.util import verify_pass
from app.models import audit, bag, distvendor, sku, auditsku, bagtosku, audittobag, disttobag
from app import db
import datetime



audited_object = {
    "distributor_id" : "1",
    "auditor_id" : "6",
    "latitude" : "30.85",
    "longnitude" : "75.85",
    "bags" : [
         {
            "bag_uid" : "MDZ0890000002",
            "bag_weight" : "25",
            "sku" : [
                {
                    "sku_asn_number" : "ASN0890000001",
                    "sku_id" : "1",
                    "sku_weight" : "2"
                },
                {
                    "sku_asn_number" : "ASN0890000002",
                    "sku_id" : "2",
                    "sku_weight" : "4"
                }
                
            ]
            
        },
        
        {
            "bag_uid" : "MDZ0890000002",
            "bag_weight" : "25",
            "sku" : [
                {
                    "sku_asn_number" : "ASN0890000001",
                    "sku_id" : "1",
                    "sku_weight" : "2"
                },
                {
                    "sku_asn_number" : "ASN0890000002",
                    "sku_id" : "2",
                    "sku_weight" : "4"
                },
                {
                    "sku_asn_number" : "ASN0890000002",
                    "sku_id" : "",
                    "sku_weight" : "4",
                    "sku_name" : "testingsku"
                }

                
            ]
            
        }
        
        

    ]
}



@blueprint.route('/create_audit', methods=['GET', 'POST'])
def create_audit():
    import time
    # checking query parameters
    try:
        start_time = time.time()
        data = request.get_json(force=True)
        print(data)
        audit_temp = data
        auditor_id, distributor_id = data['auditor_id'], data['distributor_id']
        latitude, longnitude = data["latitude"], data["longnitude"]
        bags = data["bags"]
    except Exception as e:
        print(e)
        return jsonify(status=500,message="something wrong with query parameter!")
    # create new audit
    try:
        audit_id = audit(dist_id=distributor_id,auditor_id=auditor_id,latitude=latitude,
                    longnitude=longnitude, created_at = datetime.datetime.now(), status = "incomplete")
        db.session.add(audit_id)
        db.session.commit()
    except Exception as e:
        print(e)
        return jsonify(status=500,message="audit cannot be created!")
    audited_bags = []
    try:
        if audit_id is not None:
            if bags is not None and len(bags) != 0:
                for audited_bag in bags:
                    try:
                        temp = audited_bag
                        bag_uid = audited_bag["bag_uid"]
                        bag_weight = audited_bag["bag_weight"]
                        # check if bag weight is zero
                        try:
                            if bag_weight == 0:
                                return jsonify(status=500,message="{0} Bag weight is zero".format(audited_bag["bag_uid"]))
                        except Exception as e:
                            return jsonify(status=500,message="error while measuring bag weight!")
                        # saving bag
                        bag_id = bag(uid=bag_uid,status="audited",weight=bag_weight,created_at=datetime.datetime.now())
                        db.session.add(bag_id)
                        db.session.commit()
                        temp["bag_id"] = bag_id.id
                        temp["sku_ids"] = []
                        audited_bags.append(temp)
                    except Exception as e:
                        print(e)
                        return jsonify(status=500,message="error while saving bag!")
                for audited_bag in audited_bags:
                    try:
                        temp_sku = audited_bag["sku"]
                        if len(temp_sku) == 0:
                            return jsonify(status=500,message="{0} Bag contains zero sku".format(audited_bag["bag_uid"]))
                        temp_sku_ids = []
                        for dup_sku in temp_sku:
                            sku_asn_number = dup_sku["sku_asn_number"]
                            sku_weight = dup_sku["sku_weight"]
                            sku_id = dup_sku["sku_id"]
                            # adding other sku from the app
                            try:
                                if sku_id == "":
                                    try:
                                        if sku_weight == 0:
                                            return jsonify(status=500,message="sku {0} in bag {1} weights zero".format(dup_sku["sku_name"],audited_bag["bag_uid"]))
                                    except Exception as e:
                                        print(e)
                                        return jsonify(status=500,message="error while checking zero sku weight!")
                                    try:
                                        temp_sku_id = auditsku(asn_code=sku_asn_number, weight = sku_weight,sku_name=dup_sku["sku_name"], created_at = datetime.datetime.now())
                                        db.session.add(temp_sku_id)
                                        db.session.commit()
                                        temp_sku_ids.append(temp_sku_id.id)
                                    except Exception as e:
                                        return jsonify(status=500,message="error while saving others sku!")
                           
                                else:
                                    try:
                                        if sku_weight == 0:
                                            temp_sku = sku.query.filter_by(id=sku_id).first()
                                            return jsonify(status=500,message="sku {0} in bag {1} weights zero".format(temp_sku.name,audited_bag["bag_uid"]))
                                    except Exception as e:
                                        print(e)
                                        return jsonify(status=500,message="error while checking zero sku weight!")
                                    try:
                                        temp_sku_id = auditsku(sku_id=sku_id, asn_code=sku_asn_number, weight = sku_weight, created_at = datetime.datetime.now())
                                        db.session.add(temp_sku_id)
                                        db.session.commit()
                                        temp_sku_ids.append(temp_sku_id.id)
                                    except Exception as e:
                                        print(e)
                                        return jsonify(status=500,message="error while saving master sku!")

                            except Exception as e:
                                print(e)
                                return jsonify(status=500, message="error while creating sku")
                        audited_bag["sku_ids"].append(temp_sku_ids)  
                    except Exception as e:
                        print(e)
                        return jsonify(status=500,message="error while saving sku!")

                    # audited_bag["sku_ids"] = temp_sku_ids
            # print(audited_bags)
                for audited_bag in audited_bags:
                    try:
                        temp_bag_id = audited_bag["bag_id"]
                    # print(temp_bag_id)
                    # print(audited_bag["sku_ids"])
                        try:
                            for sku_id in audited_bag["sku_ids"]:
                                for id in sku_id:
                                    bag_to_sku_id = bagtosku(bag_id=temp_bag_id,sku_id=id, created_at=datetime.datetime.now())
                                    # print(temp_bag_id, bag_to_sku_id)
                                    db.session.add(bag_to_sku_id)
                                    db.session.commit()
                        except Exception as e:
                            print(e)
                            return jsonify(status=500,message="error while mapping sku to bag!")
                            
                        audit_to_bag_id = audittobag(bag_id=temp_bag_id,audit_id=audit_id.id,created_at=datetime.datetime.now())
                        db.session.add(audit_to_bag_id)
                        db.session.commit()
                        dist_to_bag_id = disttobag(bag_id=temp_bag_id,dist_id=distributor_id,status="audited",created_at=datetime.datetime.now())
                        db.session.add(dist_to_bag_id)
                        db.session.commit()
                    except Exception as e:
                        print(e)
                        return jsonify(status=500,message="error while mapping bag!")
                return jsonify(status=200,message="audit create successfully!")
            return jsonify(status=500,message="no bags to create!")
        return jsonify(status=500,message="audit not created!")
    except Exception as e:
        print(e)
        return jsonify(status=500,message="something went wrong!")


# testing of an bag after audit by uid

@blueprint.route('/create_audit_test', methods=['GET', 'POST'])
def create_audit_test():
    data = request.get_json(force=True)
    bag_uid = data["bag_uid"]
    test_logs = []

    print("start bag testing")

    # for temp_bag in bags:
        # test 1 check if single bag of that entered in the database
    bag_count = bag.query.filter_by(uid=bag_uid).all()
    if len(bag_count) == 1:
        test_logs.append("bag count passed for {0}".format(bag_uid))
    else:
        test_logs.append("bag count failed for {0}".format(bag_uid))
    # test 2 get the audit sku count test
    print("Start sku testing")
    # temp_sku_len = len(temp_bag["sku"])
    sku_count = bagtosku.query.filter_by(bag_id=bag_count[0].id).count()
    # if sku_count == temp_sku_len:
    test_logs.append("total sku in bag {0}".format(sku_count))
    # else:
        # test_logs.append("sku failed for bag {0}".format(temp_bag["bag_uid"]))

    # test3 check if the bag status is audited or not

    if bag_count[0].status == "audited":
        test_logs.append("bag status is  {0}".format(bag_count[0].status))
    else:
        test_logs.append("bag failed status is {0}".format(bag_count[0].status))

    # test4 check if bag mapped to distributor
    temp_dist = disttobag.query.filter_by(bag_id=bag_count[0].id).all()
    if len(temp_dist) == 1:
        dist_vendor_name = distvendor.query.filter_by(id=temp_dist[0].dist_id).first()
        test_logs.append("bag mapped to distributor {0}".format(dist_vendor_name.vendor_name))
    else:
        dist_vendor_name = distvendor.query.filter_by(id=temp_dist[0].dist_id).first()
        test_logs.append("bag failed mapped to distributor {0}".format(dist_vendor_name.vendor_name))

    if temp_dist[0].status == "audited":
        test_logs.append("bag stautus at distributor {0}".format(temp_dist[0].status))
    else:
        test_logs.append("success status failed to distributor for bag {0}".format(temp_dist[0].status ))


    # test5 mapped to an audit successfully

    temp_audit_bag = audittobag.query.filter_by(bag_id=bag_count[0].id).all()
    if len(temp_audit_bag) == 1:
        test_logs.append("audit id is {0}".format(temp_audit_bag[0].audit_id))
    else:
        test_logs.append("audit id is {0}".format(temp_audit_bag[0].audit_id))

    # bag weight 

    test_logs.append("bag weight is {0}".format(bag_count[0].weight))

    test_logs.append("--------testing done for ---- bag {0}".format(bag_uid))




        






    return jsonify(test_logs)