from email import message
from app.audit import blueprint
from flask_restful import Resource, Api
from flask import jsonify, render_template, redirect, request, url_for
import json
from app.base.util import verify_pass
from app.models import audit, bag, sku, auditsku, bagtosku, audittobag, disttobag
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
                }
                
            ]
            
        }
        
        

    ]
}


@blueprint.route('/create_audit', methods=['GET', 'POST'])
def create_audit():
    import time
    start_time = time.time()
    data = request.get_json(force=True)
    audit_temp = data
    auditor_id, distributor_id = data['auditor_id'], data['distributor_id']
    latitude, longnitude = data["latitude"], data["longnitude"]
    bags = data["bags"]
    # create new audit
    
    audit_id = audit(dist_id=distributor_id,auditor_id=auditor_id,latitude=latitude,
                    longnitude=longnitude, created_at = datetime.datetime.now(), status = "incomplete")
    db.session.add(audit_id)
    db.session.commit()
    audited_bags = []
    if audit_id is not None:
        if bags is not None:
            for audited_bag in bags:
                temp = audited_bag
                bag_uid = audited_bag["bag_uid"]
                bag_weight = audited_bag["bag_weight"]
                bag_id = bag(uid=bag_uid,status="audited",weight=bag_weight,created_at=datetime.datetime.now())
                db.session.add(bag_id)
                db.session.commit()
                temp["bag_id"] = bag_id.id
                temp["sku_ids"] = []
                audited_bags.append(temp)
            for audited_bag in audited_bags:
                temp_sku = audited_bag["sku"]
                temp_sku_ids = []
                for dup_sku in temp_sku:
                    sku_asn_number = dup_sku["sku_asn_number"]
                    sku_weight = dup_sku["sku_weight"]
                    sku_id = dup_sku["sku_id"]
                    temp_sku_id = auditsku(sku_id=sku_id, asn_code=sku_asn_number, weight = sku_weight, created_at = datetime.datetime.now())
                    db.session.add(temp_sku_id)
                    db.session.commit()
                    temp_sku_ids.append(temp_sku_id.id)
                audited_bag["sku_ids"].append(temp_sku_ids)  
                # audited_bag["sku_ids"] = temp_sku_ids
        # print(audited_bags)
            for audited_bag in audited_bags:
                temp_bag_id = audited_bag["bag_id"]
                # print(temp_bag_id)
                # print(audited_bag["sku_ids"])
                for sku_id in audited_bag["sku_ids"]:
                    for id in sku_id:
                        bag_to_sku_id = bagtosku(bag_id=temp_bag_id,sku_id=id, created_at=datetime.datetime.now())
                        # print(temp_bag_id, bag_to_sku_id)
                        db.session.add(bag_to_sku_id)
                        db.session.commit()
                audit_to_bag_id = audittobag(bag_id=temp_bag_id,audit_id=audit_id.id,created_at=datetime.datetime.now())
                db.session.add(audit_to_bag_id)
                db.session.commit()
                dist_to_bag_id = disttobag(bag_id=temp_bag_id,dist_id=distributor_id,status="audited",created_at=datetime.datetime.now())
                db.session.add(dist_to_bag_id)
                db.session.commit()
            return jsonify(status=200,message="audit create successfully")
        # raise ValueError(audited_bags)
        # sku_data = sku.query.all()
        # if sku_data is not None:
        #     sku_data = [dict(id=sku.id,name=sku.name,
        #                 description=sku.description,weight=sku.weight) for sku in sku_data]
        #     return jsonify(status=200,message="sku data delievered",sku_data=sku_data)
        # return jsonify(status=500,message="sku data undelievered")
        return jsonify(status=500,message="no data to save")
    return jsonify(status=500,message="no data to save")