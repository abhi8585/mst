# import json
from app import db
from app.Users import blueprint
from flask import blueprints, render_template, request, redirect, url_for, flash, session
from app.models import usertorole,role


# @blueprint.route('/')
# def list():
#     users = user.query.all()
#     roles=[]
#     for u in users:
#         if usertorole.query.filter_by(user_id=u.id).all() :
#             user_role=[]
#             for r in usertorole.query.filter_by(user_id=u.id).all():
#                 user_role.append(role.query.filter_by(id=r.role_id).first().name)
#             roles.append(user_role)
#         else:
#             roles.append([])
#     usr=zip(users,roles)
#     return render_template('user_list.html',users=usr)

# @blueprint.route('/update/<user_id>')
# def update(user_id=None):
#     if user_id:
#         user_id=int(user_id)
#         usr=user.query.filter_by(id=user_id).first()
#         usr_role=usertorole.query.filter_by(user_id=user_id).first()
#         if usr_role:
#             return render_template('user-form.html',user=usr,usr_role=usr_role.role_id)
#         return render_template('user-form.html',user=usr)
#     return render_template('user-form.html')

# @blueprint.route('/getroles', methods=['GET'])
# def getroles():
#     roles=role.query.all()
#     return json.dumps(dict(roles=[ [r.id,r.name] for r in roles]))

# @blueprint.route('/update', methods=['POST'])
# def save():
#     user_id=request.form.get('user_id')
#     username=request.form.get('username')
#     firstname=request.form.get('firstname')
#     lastname=request.form.get('lastname')
#     email=request.form.get('email')
#     role_id=request.form.get('role')
#     phone_no=request.form.get('phone_no')
#     if user_id: #update
#         try:
#             user_id=int(user_id)
#             usr=user.query.filter_by(id=user_id).first()
#             usr.name=username
#             usr.first_name=firstname
#             usr.last_name=lastname
#             usr.email=email
#             usr.phone_number=phone_no
#             if role_id:
#                 user_role=usertorole.query.filter_by(user_id=user_id).first()
#                 if user_role:
#                     user_role.role_id=int(role_id)
#                 else:
#                     usr_role=usertorole(user_id=usr.id,role_id=role_id)
#                     db.session.add(usr_role)
#             db.session.commit()
#             return json.dumps(dict(status='success',msg='User updated successfully'))
#         except Exception as e:
#             print(e)
#             return json.dumps(dict(status='error',msg='User not updated'))
#     return json.dumps(dict(status='error',msg='User id not found'))

# @blueprint.route('/delete')
# def delete():
#     user_id=request.args.get('user_id')
#     if user_id:
#         try:
#             user_id=int(user_id)
#             usr=user.query.filter_by(id=user_id).first()
#             usr_role=usertorole.query.filter_by(user_id=user_id).first()
#             db.session.delete(usr)
#             db.session.delete(usr_role)
#             db.session.commit()
#             return json.dumps(dict(status='success',msg='User deleted successfully'))
#         except Exception as e:
#             print(e)
#             return json.dumps(dict(status='error',msg='User not deleted'))
#     return json.dumps(dict(status='error',msg='User id not found'))