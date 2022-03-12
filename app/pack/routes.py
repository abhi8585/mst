# -*- encoding: utf-8 -*-
"""
Copyright (c) 2021
"""
from app.pack import blueprint
from app.models import role, usertorole
from .. import db
from decouple import config
import json, requests
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response
import pdfkit
import os
from flask_restful import Resource, Api

# @blueprint.route('/list')
# def list():
#     packages = package.query.all()
#     return render_template('package-list.html', packages=packages)


# # routes for addding new auditor
# @blueprint.route('/list/auditor')
# def listauditor():
#     packages = package.query.all()
#     return render_template('auditor-list.html', packages=packages)

# @blueprint.route('/new/<auditor_id>')
# @blueprint.route('/new/auditor')
# def createauditor(package_id=0):
#     if int(package_id) > 0:
#         package_detail = package.query.filter_by(id=package_id).first()
#         if not package_id:
#             render_template('404')
#         return render_template('package-form.html', package_detail=package_detail, config=config)
#     return render_template('auditor-form.html', config=config)

#   ----- register new destruction centre

# @blueprint.route('/list/destruction')
# def listdestruction():
#     packages = package.query.all()
#     return render_template('destruction-list.html', packages=packages)

# @blueprint.route('/new/<destruction_id>')
# @blueprint.route('/new/destruction')
# def createdestruction(package_id=0):
#     if int(package_id) > 0:
#         package_detail = package.query.filter_by(id=package_id).first()
#         if not package_id:
#             render_template('404')
#         return render_template('destruction-form.html', package_detail=package_detail, config=config)
#     return render_template('destruction-form.html', config=config)



# @blueprint.route('/pdf/<package_id>')
# def pdf(package_id):
#     if int(package_id)>0:
#         package_detail=package.query.filter_by(id=package_id).first()
#         thumbnail=package_detail.thumbnail_image.split(',')
#         n=len(thumbnail)
#         rendered=render_template('pack-pdf.html', package_detail=package_detail,thumbnails=thumbnail,n=n)
#         pdf= pdfkit.from_string(rendered, False)
#         response=make_response(pdf)
#         response.headers['Content-Type']="application/pdf"
#         response.headers['Content-Dispositions']='attachment; filename=package.pdf'
#         return response



# @blueprint.route('/new/<package_id>')
# @blueprint.route('/new/')
# def create(package_id=0):
#     if int(package_id) > 0:
#         package_detail = package.query.filter_by(id=package_id).first()
#         if not package_id:
#             render_template('404')
#         return render_template('package-form.html', package_detail=package_detail, config=config)
#     return render_template('package-form.html', config=config)

# @blueprint.route("/get/blogcategory", methods=['GET'])
# def getBlogCategory():
#     pack_categories = packagecategory.query.all()
#     pack_categories = [{"id": category.id, 'name': category.name} for category in pack_categories]
#     return json.dumps(dict(status=200,categories=pack_categories))

# #To insert or update an Package
# @blueprint.route("/insert/package",methods=['POST'])
# def insertPackage():
#     import uuid
#     from app.services.S3 import FileUploadService
#     from ..models import gallery, package, user,packagecategory
#     # check if the request is for update or insert
#     package_id = int(request.form.get('package_id', 0))
 
    
#     if package_id == None or '':
#         return json.dumps(dict(status=400,message='Category is not given')), 400
 
#     title = request.form['title']
#     if title == None or '':
#         return json.dumps(dict(status=400,message='Title is not defined')), 400
 
#     description = request.form['description']
#     if description == None or '':
#         return json.dumps(dict(status=400,message='Description is not given')), 400

    
#     location = request.form['location']
#     if location == None or '':
#         return json.dumps(dict(status=400,message='Location is not given')), 400

#     cost = request.form['cost']
#     if cost == None or '':
#         return json.dumps(dict(status=400,message='Cost is not given')), 400

#     category = request.form['category']
#     if category == None or '':
#         return json.dumps(dict(status=400,message='Category is not given')), 400

#     time_slots = request.form['time_slots']
#     if time_slots == None or '':
#         return json.dumps(dict(status=400,message='Time Slot is not given')), 400
    
#     inclusions = request.form['inclusions']
#     if inclusions == None or '':
#         return json.dumps(dict(status=400,message='Inclusions is not given')), 400
         
#     exclusions = request.form['exclusions']
#     if exclusions == None or '':
#         return json.dumps(dict(status=400,message='Exclusions is not given')), 400
    
#     terms_and_conditions = request.form['terms_and_conditions']
#     if terms_and_conditions == None or '':
#         return json.dumps(dict(status=400,message='Terms and Conditions is not given')), 400
    
#     cancellation_policy = request.form['cancellation_policy']
#     if cancellation_policy == None or '':
#         return json.dumps(dict(status=400,message='Cancellation Policy is not given')), 400
    
#     reviews = request.form['reviews']
#     if reviews == None or '':
#         return json.dumps(dict(status=400,message='Reviews is not given')),400

#     img = request.files.get('thumbnail_image')
#     if not img:
#         return json.dumps(dict(status=400,message='Thumbnail image is not given')), 400
#     img_path = None
#     if img:
#         print('asdakjsdasd')
#         filename = img.filename
#         ser=FileUploadService()
#         res=ser.upload(img,'dp-bucket')
#         if type(res) is dict:
#             raise Exception (res['error'])
#         img_path=res
    
#     if package_id != None and package_id > 0:

#         Package = package.query.filter_by(id=package_id).first()
#         Package.title = title
#         Package.description = description
#         Package.cost = cost
#         Package.location = location
#         Package.time_slots = time_slots
#         Package.terms_and_conditions = terms_and_conditions
#         Package.category = category
#         Package.inclusions = inclusions
#         Package.exclusions = exclusions
#         Package.cancellation_policy = cancellation_policy
#         Package.reviews = reviews 
#         Package.thumbnail_image=img_path
#         db.session.commit()
#         return json.dumps(dict(status=200,message="Package updated successfully",package_id=package_id))
#     pack = package(title=title, cost=cost, location=location, time_slots=time_slots, thumbnail_image=img_path,
#                     inclusions=inclusions, exclusions=exclusions, terms_and_conditions=terms_and_conditions, category=category, cancellation_policy=cancellation_policy,reviews=reviews,
#                     description=description) 
#     db.session.add(pack)
#     db.session.commit()
#     return json.dumps(dict(status=200,message="Package saved successfully",package_id=pack.id))

# # To delete a Package by ID
# @blueprint.route("/delete/package")
# def deletePackage():
#     package_id = request.args.get("package_id")
#     Package= package.query.filter_by(id=package_id).first()
#     if Package!= None:
#         Package= package.query.filter_by(id=package_id).delete()
#         db.session.commit()
#         return json.dumps(dict(status=200, message="Package deleted successfully!!"))
#     return json.dumps(dict(status=501,message="Package do not exist"))














