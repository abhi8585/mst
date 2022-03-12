from flask import redirect, url_for, render_template,jsonify
from app.enquiry import blueprint
from app.models import role, usertorole
from .. import db
from decouple import config
import json, requests,sys,boto3,tempfile
from botocore.client import Config
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response
from minio import Minio
from minio.error import S3Error
from collections import OrderedDict 
import pdfkit
import os
from datetime import date
from num2words import num2words
from sqlalchemy import func
@blueprint.route('/list')
def list():
    enq=role.query.all()
    # raise ValueError(enq)
    return render_template('enquiry_list.html',enquiry=enq)

# @blueprint.route('/installment/<enquiry_id>', methods=['POST'])
# def installment(enquiry_id):
#     largest_number=db.session.query(func.max(installments.installment_number)).filter(installments.enquiry_id == enquiry_id).first()
#     Installment=installments.query.filter_by(enquiry_id=enquiry_id).filter_by(installment_number=largest_number).first()
#     print(Installment)
#     installment_number=request.form.get('installment_number')
#     installment_date=request.form.get('installment_date')
#     payment_mode=request.form.get('payment_mode')
#     installment_amount=request.form.get('installment_amount')
#     installment_status=request.form.get('installment_status')
#     enquiry_detail=enquiry.query.filter_by(id=enquiry_id).first()
#     Package=package.query.filter_by(id=enquiry_detail.package_id).first()
#     Invoice=invoice.query.filter_by(is_active=True).filter_by(enquiry_id=enquiry_id).first()
#     print(Invoice)
#     if(Installment==None):
#         amount=Invoice.cost
#     else:
#         amount=Installment.pending
#     if installment_status=='Unpaid':
#         remaining_amount=int(amount)
#     else:
#         remaining_amount=int(amount)-int(installment_amount)
#     inst=installments(enquiry_id=enquiry_id,installment_number=installment_number,date=installment_date,mode=payment_mode,amount=amount,paid=installment_amount,pending=remaining_amount,status=installment_status)
#     db.session.add(inst)
#     db.session.commit()
#     return "installment added successfully"

# @blueprint.route('/edit-installment/<enquiry_id>', methods=['POST'])
# def editinstallments(enquiry_id):
#     installment_number=request.form.get("installment-number")
#     installment=installments.query.filter_by(enquiry_id=enquiry_id).filter_by(installment_number=installment_number).first()
#     installment_date=request.form.get('installment-date')
#     payment_mode=request.form.get('installment-mode')
#     installment_amount=request.form.get('installment-amount')
#     installment_status=request.form.get('installment-status')
#     installment_total=installment.amount
#     installment_pending=int(installment_total)-float(installment_amount)
#     installment.installment_number=installment_number
#     installment.date=installment_date
#     installment.mode=payment_mode
#     installment.amount=installment_total
#     installment.paid=installment_amount
#     installment.pending=installment_pending
#     installment.status=installment_status
#     db.session.commit()
#     return "installment edited successfully"

# @blueprint.route('/invoice/<enquiry_id>', methods=['POST'])
# def Invoice(enquiry_id):
#         print(request.form)
#         total_cost=0
#         n=int(request.form.get('inclusions'))
#         inclusions={}
#         for i in range(1,n+1):
#             if request.form.get('incl'+str(i)+'_name')!=None or request.form.get('incl'+str(i)+'_name')!='':
#                 globals()[f"incl{i}name"] = request.form.get('incl'+str(i)+'_name')
#                 globals()[f"incl{i}qty"] = request.form.get('incl'+str(i)+'_qty',1)
#                 globals()[f"incl{i}amount"] = request.form.get('incl'+str(i)+'_amount',0)
#                 total_cost=total_cost+int(globals()[f"incl{i}amount"])
#                 inclusions[globals()[f"incl{i}name"]]= [globals()[f"incl{i}amount"],globals()[f"incl{i}qty"]]
#         m=0
#         if int(enquiry_id)>0:
#             invoices=invoice.query.filter_by(enquiry_id=enquiry_id).all()
#             if(len(invoices)==0):
#                 version=1
#                 m=1
#             else:
#                 invoi=invoice.query.filter_by(is_active=True).first()
#                 version=invoi.version+1
#                 last_id=invoi.id
#             enquiry_detail=enquiry.query.filter_by(id=enquiry_id).first()
#             Package=package.query.filter_by(id=enquiry_detail.package_id).first()
#             today=date.today()
#             total_cost=total_cost+int(Package.cost)
#             cgst=(9/100)*total_cost
#             sgst=(9/100)*total_cost
#             final_total=total_cost+cgst+sgst
#             words=num2words(final_total)
#             if m==0:
#                 invo=invoice.query.filter_by(id=last_id).first()
#                 invo.is_active=False

#                 db.session.commit()
#             inv=invoice(date=today,enquiry_id=enquiry_id,customer_name=enquiry_detail.name,cost=final_total,version=version, is_active=True)
#             db.session.add(inv)
#             db.session.commit()
#             Invoice=invoice.query.filter_by(is_active=True).first()
            
#             rendered=render_template('invoice.html', enquiry_detail=enquiry_detail, package_detail=Package, inclusions=inclusions, number=n, time=today, word=words, sub_total=total_cost, invoice=Invoice,cgst=cgst,sgst=sgst, total=final_total)
#             pdf= pdfkit.from_string(rendered, False)
#             response=make_response(pdf)
#             response.headers['Content-Type']="application/pdf"
#             response.headers['Content-Dispositions']='attachment; filename=invoice.pdf'
            
#             return response 

# @blueprint.route('/upload_to_s3/', methods=['POST'])
# def upload_to_s3():
#     file = request.files.get('file')
#     inv_id=request.form.get('invoice_id')
#     if file:
#         try:
#             client=S3.FileUploadService()
#             resp=client.upload(file,'dp-docs')
#             inv=invoice.query.filter_by(id=inv_id).first()
#             inv.link=resp
#             db.session.commit()
#             return "File uploaded successfully"
#         except Exception as e:
#             return jsonify({"message":str(e)})
#     return jsonify({"message":"no file found"})
# @blueprint.route('/new/<enquiry_id>')
# @blueprint.route('/new/')
# def create(enquiry_id=0):
#     if int(enquiry_id) > 0:
#         enquiry_detail = enquiry.query.filter_by(id=enquiry_id).first()
#         installment = installments.query.filter_by(enquiry_id=enquiry_id).all()
#         Invoice=invoice.query.filter_by(is_active=True).filter_by(enquiry_id=enquiry_id).first()
#         if not enquiry_detail:
#             render_template('404')
#         return render_template('enquiry_form.html', enquiry_detail=enquiry_detail, config=config, installment=installment, invoice=Invoice)
#     return render_template('enquiry_form.html', config=config)




@blueprint.route("/insert/role",methods=['GET', 'POST'])
def insertRole():
    role_name = request.form['role_name']
    if role_name == None or role_name=='':
        return json.dumps(dict(status=400,message='role name is not defined')), 400 

    new_role = role(name=role_name,description='abhishek')
    db.session.add(new_role)
    db.session.commit()
    enq=role.query.all()
    # return render_template('enquiry_list.html',enquiry=enq)
    return json.dumps(dict(status=200,message='role created successfully!')), 200

# @blueprint.route("/insert/enquiry",methods=['GET', 'POST'])
# def insertEnquiry():
#     import uuid
#     from ..models import enquiry
#     # check if the request is for update or insert
#     enquiry_id = int(request.form.get('enquiry_id', 0))
#     if enquiry_id == None or enquiry_id=='':
#         return json.dumps(dict(status=400,message='enquiry id is not given')), 400    
#     # check if the title is given
#     name = request.form['name']
#     if name == None or name=='':
#         return json.dumps(dict(status=400,message='name is not defined')), 400
#     # check if the description is given
#     email = request.form['email']
#     if email == None or email=='':
#         return json.dumps(dict(status=400,message='email is not given')), 400
    
#     phone = request.form['phone']
#     if phone == None or phone=='':
#         return json.dumps(dict(status=400,message='phone is not given')), 400
    
#     date = request.form['date']
#     if date == None or date=='':
#         return json.dumps(dict(status=400,message='date is not given')), 400
    
#     location = request.form['location']
#     if location == None or location=='':
#         return json.dumps(dict(status=400,message='location is not given')), 400
    
#     budget = request.form['budget']
#     if budget == None or budget=='':
#         return json.dumps(dict(status=400,message='budget is not given')), 400
    
#     package_id=request.form['package_id']
#     if package_id == None or package_id=='':
#         package_id=None

#     blog_id=request.form['blog_id']
#     if blog_id == None or blog_id=='':
#         blog_id=None

#     status = request.form['status']
#     if status == None or status=='':
#         status=None

#     import datetime
#     if enquiry_id != None and enquiry_id > 0:
#         enquiry = enquiry.query.filter_by(id=enquiry_id).first()
#         enquiry.name = name
#         enquiry.email=email
#         enquiry.phone_number=phone
#         enquiry.budget=budget
#         enquiry.location=location
#         enquiry.created_at=date
#         enquiry.updated_at=datetime.datetime.now()
#         enquiry.package_id=package_id
#         enquiry.blog_id=blog_id
#         enquiry.status=status
        
#         db.session.commit()
#         return json.dumps(dict(status=200,message="enquiry updated successfully",enquiry_id=enquiry_id))
#     Enquiry = enquiry(email=email,location=location,phone_number=phone,budget=budget,created_at=date,booking_date=date,updated_at=datetime.datetime.now(),package_id=package_id,status=status,blog_id=blog_id,name=name)
    
#     db.session.add(Enquiry)
#     db.session.commit()
#     return json.dumps(dict(status=200,message="enquiry saved successfully",enquiry_id=Enquiry.id))

# @blueprint.route("/delete/enquiry")
# def deleteenquiry():
#     enquiry_id = request.args.get("enquiry_id")
#     Enquiry= enquiry.query.filter_by(id=enquiry_id).first()
#     if Enquiry != None:
#         Enquiry = enquiry.query.filter_by(id=enquiry_id).delete()
#         db.session.commit()
#         return json.dumps(dict(status=200, message="enquiry deleted successfully!!"))
#     return json.dumps(dict(status=501,message="enquiry do not exist"))
