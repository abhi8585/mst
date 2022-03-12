# -*- encoding: utf-8 -*-
"""
Copyright (c) 2021
"""
from flask import redirect, url_for, render_template
from app.blog import blueprint
from app.models import userinfo, role, usertorole
from .. import db
from decouple import config
import json, requests,sys,boto3,tempfile
from botocore.client import Config
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response
from minio import Minio
from minio.error import S3Error
from app.base.models import User
from app.base.util import hash_pass

@blueprint.route('/list')
def list():
    users = userinfo.query.all()
    # page = request.args.get('page', 1, type=int)
    # blogs = blog.query.order_by(blog.created_at.desc()).paginate(
    #     page, 10, False
    # )
    # next_url = url_for('list', page=blogs.next_num) \
    #     if blogs.has_next else None
    # prev_url = url_for('list', page=blogs.prev_num) \
    #     if blogs.has_prev else None
    return render_template('blog-list.html', users=users)

 # function to get image from minio

# @blueprint.route('/new/<blog_id>')
# @blueprint.route('/new/')
# def create(blog_id=0):
#     if int(blog_id) > 0:
#         blog_detail = blog.query.filter_by(id=blog_id).first()
#         if not blog_detail:
#             render_template('404')
#         return render_template('blog-form.html', blog_detail=blog_detail, config=config)
#     roles_details = role.query.all()
#     roles = [role.name for role in roles_details]
#     # raise ValueError(roles)
#     return render_template('blog-form.html', roles=roles,config=config)

    
#used to insert the user
@blueprint.route("/insert/user",methods=['GET', 'POST'])
def insertUser():
    import string    
    import random
    user_name = request.form['user_name']
    user_email = request.form['user_email']
    # user_password = request.form['user_password']
    user_role_name = request.form['user_role_name']
    user_password = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))
    print(user_password)
    user_password_bytes  = hash_pass(user_password)
    new_user_login = User(username=user_name,email=user_email,password=user_password)
    db.session.add(new_user_login)
    db.session.commit()
    new_user=userinfo(name=user_name,password=user_password_bytes,email=user_email)
    db.session.add(new_user)
    db.session.commit()
    new_user_id = new_user.id
    get_role_id = role.query.filter_by(name=user_role_name).first().id
    user_role_mapping = usertorole(user_id=new_user_id, role_id=get_role_id)
    db.session.add(user_role_mapping)
    db.session.commit()
    return json.dumps(dict(user_id='User added successfully!!'))



#To insert or update an blog
# import datetime
# @blueprint.route("/insert/blog",methods=['GET', 'POST'])
# def insertBlog():
#     import uuid
#     from app.services.S3 import FileUploadService
#     from ..models import gallery, blogcategory, blog, user
#     # check if the request is for update or insert
#     blog_id = int(request.form.get('blog_id', 0))
#     author_id = request.form['author_id']
#     if author_id == None or '':
#         return json.dumps(dict(status=400,message='Author is not given')), 400
#     # check if the category is given
#     category_id = request.form['category_id']
#     if category_id == None or '':
#         return json.dumps(dict(status=400,message='Category is not given')), 400
#     # check if the number of claps is given
#     claps = request.form['claps']
#     if claps == None or '':
#         return json.dumps(dict(status=400,message='Claps is not given')),400
#     # check if the title is given
#     title = request.form['title']
#     if title == None or '':
#         return json.dumps(dict(status=400,message='Title is not defined')), 400
#     # check if the tags are given
#     tags = request.form.get('tags', "").split(",")
#     if not tags:
#         return json.dumps(dict(status=400,message='Tags are not given')), 400
#     # check if the description is given
#     description = request.form['description']
#     if description == None or '':
#         return json.dumps(dict(status=400,message='Description is not given')), 400
#     # getting the thumbnail image for the blog.
#     img = request.files.get('thumbnail_image')
#     if not img and not blog_id:
#         return json.dumps(dict(status=400,message='Thumbnail image is not given')), 400
#     img_path = None
#     if img:
#         filename = img.filename
#         ser=FileUploadService()
#         res=ser.upload(img,'dp-bucket')
#         if type(res) is dict:
#             raise Exception (res['error'])
#         img_path=res
#     publish = bool(int(request.form['publish']))
#     print(publish, request.form['publish'])
#     # getting the created_at time
#     created_at = datetime.datetime.now()
#     # getting the udpated_at time
#     updated_at = datetime.datetime.now()

#     # check if the title is duplicate 
#     title_check = blog.query.filter_by(title=title).first()
#     if blog_id and title_check and blog_id != title_check.id:
#         return json.dumps(dict(status=409,message="Title must be unique")), 409
#     if not blog_id and title_check:
#         return json.dumps(dict(status=409,message="Title must be unique")), 409
        
#     if blog_id != None and blog_id > 0:
#         blog = blog.query.filter_by(id=blog_id).first()
#         blog.author_id = author_id
#         blog.category_id = category_id
#         blog.claps = claps
#         blog.title = title
#         blog.description = description
#         if img_path:
#             blog.thumbnail_image = img_path
#         blog.tags = tags
#         blog.published = publish
#         blog.updated_at = datetime.datetime.now()
#         db.session.commit()
#         return json.dumps(dict(status=200,message="Blog updated successfully",blog_id=blog_id))
#     blog_id = blog(author_id=author_id,category_id=category_id,claps=claps,title=title,
#                     description=description,thumbnail_image=img_path,tags=tags, published=publish, created_at=created_at,updated_at=updated_at)
    
#     db.session.add(blog_id)
#     db.session.commit()
#     return json.dumps(dict(status=200,message="Blog saved successfully",blog_id=blog_id.id))

# # To delete a blog by ID
# @blueprint.route("/delete/blog")
# def deleteBlog():
#     blog_id = request.args.get("blog_id")
#     blog_id = blog.query.filter_by(id=blog_id).first()
#     if blog_id != None:
#         blog_id = blog.query.filter_by(id=blog_id.id).delete()
#         db.session.commit()
#         return json.dumps(dict(status=200, message="Blog deleted successfully!!"))
#     return json.dumps(dict(status=501,message="BLog do not exist"))

# # To insert the Author
# @blueprint.route("/insert/author")
# def insertAuthor():
#     author_name = request.form['author_name']
#     raise ValueError(author_name)

# # To insert the role 
# @blueprint.route("/insert/role", methods=['GET','POST'])
# def insertRole():
#     role_name, role_description = request.form["role_name"],request.form["role_description"]
#     role_id = role(name=role_name, description=role_description)
#     if role_id:
#         db.session.add(role_id)
#         db.session.commit()
#         return json.dumps(dict(status=200,message="Role added successfully"))



# # To get all the Blog Categories
# @blueprint.route("/get/blogcategory", methods=['GET'])
# def getBlogCategory():
#     blog_categories = blogcategory.query.all()
#     blog_categories = [{"id": category.id, 'name': category.name} for category in blog_categories]
#     return json.dumps(dict(status=200,categories=blog_categories))


# #To test and learn the joins in SQLALCHEMY
# @blueprint.route("/get/BlogCategoryData")
# def categoryData():
#     # return 'Hello'
#     category_data = db.session.query(blog,blogcategory).join(blogcategory).all()
#     blog_data = [blog.id for blog, category in category_data ]
#     return json.dumps(dict(data=blog_data))

# # To get the list of Blog Authors
# @blueprint.route("/get/author")
# def getAuthor():
#     role_name = "Author"
#     role_data = role.query.filter_by(name=role_name).first()
#     user_info = []
#     if role_data:
#         user_have_role_data = usertorole.query.filter_by(role_id=role_data.id).all()
#         user_data = [user.user_id for user in user_have_role_data]
#         query = user.query.filter(user.id.in_(user_data)).all()
#         user_info = [dict(name=user.name,id=user.id) for user in query]
#     # user_have_role_data = db.session.query(usertorole,user).join(user).all()
#     return json.dumps(dict(status=200,authors=user_info))

# # To test the upload image feature



# # To add an user in databse
# @blueprint.route("/save/user",methods=['GET',"POST"])
# def saveUser():
#     name, email, phone = request.form['name'], request.form['email'], request.form['phone']
#     password, first_name, last_name = request.form['password'], request.form['first_name'], request.form['last_name']
#     # raise ValueError([name,email,phone,last_name,first_name,phone,password])
#     user_id = user(name=name, email=email, phone_number=phone,
#                 password=password,first_name=first_name,last_name=last_name)
#     db.session.add(user_id)
#     db.session.commit()
#     return json.dumps(dict(status=200,message='User added successfully'))

# # To get the Users data
# @blueprint.route("/get/user")
# def getUser():
#     user_data = user.query.all()
#     user_data = [user.id for user in user_data]
#     return json.dumps(dict(data=user_data))

# # To get the role data 
# @blueprint.route("/get/role")
# def getRole():
#     role_data = role.query.all()
#     role_data = [role.id for role in role_data]
#     return json.dumps(dict(data=role_data))

# # Insert the role and user
# @blueprint.route("/give/usertorole")
# def giveUserToRole():
#     user_id, role_id = 10, 1
#     user_to_role = usertorole(user_id=user_id,role_id=role_id)
#     db.session.add(user_to_role)
#     db.session.commit()
#     return json.dumps(dict(message="Role is assigned to User"))


# @blueprint.route("/image-gallery")
# def image_gallery():
#     return render_template('image-gallery.html')

# @blueprint.route("/all-images/")
# def all_images():
#     gallery_id = request.args['gallery_id']
#     images = image.query.join(imagetogallery, imagetogallery.image_id == image.id).join(gallery, gallery.id == imagetogallery.gallery_id)\
#     .filter(gallery.id == gallery_id)
#     response_data = []
#     for db_image in images:
#         response_data.append({
#             "id": db_image.id,
#             "url": "{}{}".format(config('HOST'), db_image.url)
#         })
#     return json.dumps({'status': "success", "imageList": response_data})

