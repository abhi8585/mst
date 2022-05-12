from datetime import datetime
from enum import unique
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin
# from app.exceptions import ValidationError
from . import db, login_manager
from sqlalchemy_serializer import SerializerMixin


class permission(db.Model):
    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)



class roletopermission(db.Model):
    __tablename__ = 'roletopermission'

    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.ForeignKey('role.id'), nullable=False)
    permission_id = db.Column(db.ForeignKey('permissions.id'), nullable=False)

    permission = db.relationship('permission', primaryjoin='roletopermission.permission_id == permission.id', backref='role_to_permissions')
    role = db.relationship('role', primaryjoin='roletopermission.role_id == role.id', backref='role_to_permissions')


class userinfo(db.Model):
    __tablename__ = 'user_info'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    password =  db.Column(db.Binary)
    email = db.Column(db.String(250))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone_number = db.Column(db.String(50))

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"



class usertorole(db.Model):
    __tablename__ = 'usertorole'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user_info.id'), nullable=False)
    role_id = db.Column(db.ForeignKey('role.id'), nullable=False)

    # role = db.relationship('role', primaryjoin='usertorole.role_id == role.id', backref='user_to_roles')
    # User = db.relationship('user_info', primaryjoin='usertorole.user_id == user_info.id', backref='user_to_roles')


# Distributor Table
class distributor(db.Model):
    __tablename__ = 'distributor'
    id = db.Column(db.Integer, primary_key=True)
    vendor_code = db.Column(db.String(50), nullable=False)
    vendor_name = db.Column(db.String(250), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    pin_code = db.Column(db.String(25), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.String(50), nullable=False)
    longnitude = db.Column(db.String(50), nullable=False)
    contact_person = db.Column(db.String(50), nullable=False)
    contact_number = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    # vendor_code = db.Column(db.String(50))



class auditvendor(db.Model):
    __tablename__ = 'audit_vendor'
    id = db.Column(db.Integer, primary_key=True)
    vendor_code = db.Column(db.String(50), nullable=False)
    vendor_name = db.Column(db.String(250), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    pin_code = db.Column(db.String(25), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.String(50), nullable=False)
    longnitude = db.Column(db.String(50), nullable=False)
    contact_person = db.Column(db.String(50), nullable=False)
    contact_number = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    region_name = db.Column(db.String(50))
    # password = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())
    

class auditortovendor(db.Model):
    __tablename__ = 'auditortovendor'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user_info.id'), nullable=False)
    auditor_id = db.Column(db.ForeignKey('audit_vendor.id'), nullable=False)


class distvendor(db.Model):
    __tablename__ = 'dist_vendor'
    id = db.Column(db.Integer, primary_key=True)
    vendor_code = db.Column(db.String(50), nullable=False)
    vendor_name = db.Column(db.String(250), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    pin_code = db.Column(db.String(25), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.String(50), nullable=False)
    longnitude = db.Column(db.String(50), nullable=False)
    contact_person = db.Column(db.String(50), nullable=False)
    contact_number = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    region_name = db.Column(db.String(50))
    # password = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())


class disttovendor(db.Model):
    __tablename__ = 'disttovendor'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user_info.id'), nullable=False)
    vendor_id = db.Column(db.ForeignKey('dist_vendor.id'), nullable=False)


class sku(db.Model):
    __tablename__ = 'sku'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50))
    name = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(500))
    weight = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())


class audit(db.Model):
    __tablename__ = 'audit'
    id = db.Column(db.Integer, primary_key=True)
    dist_id = db.Column(db.ForeignKey('dist_vendor.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.String(50), nullable=False)
    longnitude = db.Column(db.String(50), nullable=False)
    auditor_id = db.Column(db.ForeignKey('user_info.id'), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())

class bag(db.Model):
    __tablename__ = 'bag'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(15), nullable=False)
    weight = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())

class auditsku(db.Model):
    __tablename__ = 'auditsku'
    id = db.Column(db.Integer, primary_key=True)
    sku_id = db.Column(db.ForeignKey('sku.id'))
    sku_name= db.Column(db.String(50))
    asn_code = db.Column(db.String(50))
    weight = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())


class audittobag(db.Model):
    __tablename__ = 'audit_to_bag'

    id = db.Column(db.Integer, primary_key=True)
    audit_id = db.Column(db.ForeignKey('audit.id'), nullable=False)
    bag_id = db.Column(db.ForeignKey('bag.id'), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())


class disttobag(db.Model):
    __tablename__ = 'dist_to_bag'

    id = db.Column(db.Integer, primary_key=True)
    dist_id = db.Column(db.ForeignKey('dist_vendor.id'), nullable=False)
    bag_id = db.Column(db.ForeignKey('bag.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())

class bagtosku(db.Model):
    __tablename__ = 'bag_to_audit_sku'

    id = db.Column(db.Integer, primary_key=True)
    bag_id = db.Column(db.ForeignKey('bag.id'), nullable=False)
    sku_id = db.Column(db.ForeignKey('auditsku.id'), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())


class pickup(db.Model):
    __tablename__ = 'pickup'
    id = db.Column(db.Integer, primary_key=True)
    transporter_id = db.Column(db.ForeignKey('user_info.id'), nullable=False)
    truck_number= db.Column(db.String(25))
    lr_number= db.Column(db.String(50))
    latitude = db.Column(db.String(50), nullable=False)
    longnitude = db.Column(db.String(50), nullable=False)
    dist_id = db.Column(db.ForeignKey('dist_vendor.id'), nullable=False)
    status = db.Column(db.String(25))
    pickup_number = db.Column(db.String(50))
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())


class picktobag(db.Model):
    __tablename__ = 'pick_to_bag'
    id = db.Column(db.Integer, primary_key=True)
    bag_id = db.Column(db.ForeignKey('bag.id'), nullable=False)
    pick_id = db.Column(db.ForeignKey('pickup.id'), nullable=False)
    status = db.Column(db.String(25))
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())



# for transport vendor

class transportvendor(db.Model):
    __tablename__ = 'transport_vendor'
    id = db.Column(db.Integer, primary_key=True)
    vendor_code = db.Column(db.String(50), nullable=False)
    vendor_name = db.Column(db.String(250), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    pin_code = db.Column(db.String(25), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.String(50), nullable=False)
    longnitude = db.Column(db.String(50), nullable=False)
    contact_person = db.Column(db.String(50), nullable=False)
    contact_number = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    region_name = db.Column(db.String(50))
    # password = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())


class transtovendor(db.Model):
    __tablename__ = 'transtovendor'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user_info.id'), nullable=False)
    vendor_id = db.Column(db.ForeignKey('transport_vendor.id'), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())


class deviatedbag(db.Model):
    __tablename__ = 'deviated_bag'

    id = db.Column(db.Integer, primary_key=True)
    bag_id = db.Column(db.ForeignKey('bag.id'), nullable=False)
    pick_id = db.Column(db.Integer,  nullable=False)
    weight = db.Column(db.String(10), nullable=False)
    remarks = db.Column(db.String(500))
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())



# depo vendor tables

class depovendor(db.Model):
    __tablename__ = 'depo_vendor'
    id = db.Column(db.Integer, primary_key=True)
    vendor_code = db.Column(db.String(50), nullable=False)
    vendor_name = db.Column(db.String(250), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    pin_code = db.Column(db.String(25), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.String(50), nullable=False)
    longnitude = db.Column(db.String(50), nullable=False)
    contact_person = db.Column(db.String(50), nullable=False)
    contact_number = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    region_name = db.Column(db.String(50))
    # password = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())

class depotomaster(db.Model):
    __tablename__ = 'depo_to_master'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user_info.id'), nullable=False)
    vendor_id = db.Column(db.ForeignKey('depo_vendor.id'), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())


class depotopicker(db.Model):
    __tablename__ = 'depo_to_picker'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user_info.id'), nullable=False)
    vendor_id = db.Column(db.ForeignKey('depo_vendor.id'), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())


class depoinventory(db.Model):
    __tablename__ = 'depo_inventory'

    id = db.Column(db.Integer, primary_key=True)
    submitted_by = db.Column(db.ForeignKey('user_info.id'), nullable=False)
    depo_id = db.Column(db.ForeignKey('depo_vendor.id'), nullable=False)
    bag_id = db.Column(db.ForeignKey('bag.id'), nullable=False)
    status = db.Column(db.String(25))
    latitude = db.Column(db.String(50))
    longnitude = db.Column(db.String(50))
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())



class deviateddepobag(db.Model):
    __tablename__ = 'deviated_depo_bag'

    id = db.Column(db.Integer, primary_key=True)
    bag_id = db.Column(db.ForeignKey('bag.id'), nullable=False)
    weight = db.Column(db.String(10), nullable=False)
    remarks = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())


class depopickup(db.Model):
    __tablename__ = 'depo_pickup'
    id = db.Column(db.Integer, primary_key=True)
    picker_id = db.Column(db.ForeignKey('user_info.id'), nullable=False)
    truck_number= db.Column(db.String(50))
    lr_number= db.Column(db.String(25))
    latitude = db.Column(db.String(50), nullable=False)
    longnitude = db.Column(db.String(50), nullable=False)
    depo_id = db.Column(db.ForeignKey('depo_vendor.id'), nullable=False)
    deviated_weight = db.Column(db.String(10))
    status = db.Column(db.String(25))
    asn_number = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())


class depopicktobag(db.Model):
    __tablename__ = 'depo_pick_to_bag'
    id = db.Column(db.Integer, primary_key=True)
    bag_id = db.Column(db.ForeignKey('bag.id'), nullable=False)
    pick_id = db.Column(db.ForeignKey('depo_pickup.id'), nullable=False)
    status = db.Column(db.String(25))
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())


class deviateddepopickbag(db.Model):
    __tablename__ = 'deviated_depo_pick_bag'

    id = db.Column(db.Integer, primary_key=True)
    bag_id = db.Column(db.ForeignKey('bag.id'), nullable=False)
    weight = db.Column(db.String(10), nullable=False)
    remarks = db.Column(db.String(500))
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())


class destructionvendor(db.Model):
    __tablename__ = 'destruction_vendor'
    id = db.Column(db.Integer, primary_key=True)
    vendor_code = db.Column(db.String(50), nullable=False)
    vendor_name = db.Column(db.String(250), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    pin_code = db.Column(db.String(25), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.String(50), nullable=False)
    longnitude = db.Column(db.String(50), nullable=False)
    contact_person = db.Column(db.String(50), nullable=False)
    contact_number = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    region_name = db.Column(db.String(50))
    # password = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())

class destructiontomaster(db.Model):
    __tablename__ = 'destruction_to_master'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user_info.id'), nullable=False)
    vendor_id = db.Column(db.ForeignKey('destruction_vendor.id'), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())


class destructioninventory(db.Model):
    __tablename__ = 'destruction_inventory'

    id = db.Column(db.Integer, primary_key=True)
    submitted_by = db.Column(db.ForeignKey('user_info.id'), nullable=False)
    destruction_id = db.Column(db.ForeignKey('destruction_vendor.id'), nullable=False)
    bag_id = db.Column(db.ForeignKey('bag.id'), nullable=False)
    status = db.Column(db.String(25))
    latitude = db.Column(db.String(50))
    longnitude = db.Column(db.String(50))
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())



class deviateddestructionbag(db.Model):
    __tablename__ = 'deviated_destruction_bag'

    id = db.Column(db.Integer, primary_key=True)
    bag_id = db.Column(db.ForeignKey('bag.id'), nullable=False)
    weight = db.Column(db.String(10), nullable=False)
    remarks = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime())

