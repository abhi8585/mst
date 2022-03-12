from flask import redirect, url_for, render_template
from app.category import blueprint
from app.models import role, usertorole
from .. import db
from decouple import config
import json, requests,sys,boto3,tempfile
from botocore.client import Config
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response
from minio import Minio
from minio.error import S3Error

# @blueprint.route('/list')
# def list():
#     # category=blogcategory.query.all()
#     return render_template('category-list.html',categories=category)

# @blueprint.route('/new/<category_id>')
# @blueprint.route('/new/')
# def create(category_id=0):
#     if int(category_id) > 0:
#         category_detail = blogcategory.query.filter_by(id=category_id).first()
#         if not category_detail:
#             render_template('404')
#         return render_template('category-form.html', category_detail=category_detail, config=config)
#     return render_template('category-form.html', config=config)

# import datetime
# @blueprint.route("/insert/category",methods=['GET', 'POST'])
# def insertCategory():
#     import uuid
#     from app.services.S3 import FileUploadService
#     from ..models import blogcategory
#     # check if the request is for update or insert
#     category_id = int(request.form.get('category_id', 0))
#     if category_id == None or '':
#         return json.dumps(dict(status=400,message='Category is not given')), 400    
#     # check if the title is given
#     title = request.form['title']
#     if title == None or '':
#         return json.dumps(dict(status=400,message='Title is not defined')), 400
#     # check if the description is given
#     description = request.form['description']
#     if description == None or '':
#         return json.dumps(dict(status=400,message='Description is not given')), 400
#     img = request.files.get('thumbnail_image')
#     if not img:
#         return json.dumps(dict(status=400,message='Thumbnail image is not given')), 400
#     img_path = None
#     if img:
#         filename = img.filename
#         ser=FileUploadService()
#         res=ser.upload(img,'dp-bucket')
#         if type(res) is dict:
#             raise Exception (res['error'])
#         img_path=res
#     #publish = bool(int(request.form['publish']))

#     # check if the title is duplicate 
#     title_check = blogcategory.query.filter_by(name=title).first()
#     if category_id and title_check and category_id != title_check.id:
#         return json.dumps(dict(status=409,message="Title must be unique")), 409
#     if not category_id and title_check:
#         return json.dumps(dict(status=409,message="Title must be unique")), 409
        
#     if category_id != None and category_id > 0:
#         Category = blogcategory.query.filter_by(id=category_id).first()
#         Category.name = title
#         Category.description = description
#         Category.thumbnail_image = img_path
#         db.session.commit()
#         return json.dumps(dict(status=200,message="Category updated successfully",category_id=category_id))
#     category = blogcategory(name=title,
#                     description=description,thumbnail_image=img_path)
    
#     db.session.add(category)
#     db.session.commit()
#     return json.dumps(dict(status=200,message="Category saved successfully",category_id=category.id))

# @blueprint.route("/delete/category")
# def deleteCategory():
#     category_id = request.args.get("category_id")
#     category_id = blogcategory.query.filter_by(id=category_id).first()
#     if category_id != None:
#         category_id = blogcategory.query.filter_by(id=category_id.id).delete()
#         db.session.commit()
#         return json.dumps(dict(status=200, message="Category deleted successfully!!"))
#     return json.dumps(dict(status=501,message="Category do not exist"))