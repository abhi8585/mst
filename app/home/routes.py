# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# from sys import audit
from app.home import blueprint
from flask import jsonify, render_template, redirect, url_for
from flask_login import login_required, current_user
from app import login_manager
from jinja2 import TemplateNotFound
from app.models import depoinventory, destructioninventory, destructionvendor, disttobag, pickup, userinfo, usertorole, role
from app.models import depovendor, depotomaster, depotopicker, bag, deviateddepobag, deviateddestructionbag,deviateddepopickbag
from app.models import deviatedbag, role, transportvendor, userinfo, usertorole, auditvendor, auditortovendor, distvendor, disttovendor, sku, transportvendor, transtovendor, audit
from app import db
from sqlalchemy import and_

colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
def get_deviated_bag_count():
    bag_count = []
    bag_count.append(deviatedbag.query.count())
    bag_count.append(deviateddepobag.query.count())
    bag_count.append(deviateddepopickbag.query.count())
    bag_count.append(deviateddestructionbag.query.count())
    return bag_count

def get_bag_count():
    bag_count = []
    bag_status = ['audited', 'picked', 'collected', 'dispatched', 'received']
    for temp in bag_status:
        temp_bag_count = bag.query.filter_by(status=temp).count()
        bag_count.append(temp_bag_count)
    return bag_count


# helper function for regional distributor data

def get_audit_region():
    audit_count = []
    audit_region = ['west','east','north','south']
    for region in audit_region:
        region_count = 0
        dist_data = distvendor.query.filter_by(region_name=region).all()
        for dist in dist_data:
            audit_count_obj = audit.query.filter_by(dist_id=dist.id).count()
            region_count += audit_count_obj
        audit_count.append(region_count)
    return audit_count



@blueprint.route('/index')
@login_required
def index():
    
    bar_labels=[
    'Transporter', 'Depo Master', 'Depo picker', 'Destruction Master'
]


    # arranging data for distributor regional wise

    dist_data = distvendor.query.filter_by(region_name='west').all()
    dist_table_data = []
    for dist in dist_data:
        temp = {}
        temp['name'] = dist.vendor_name
        audit_count = audit.query.filter_by(dist_id=dist.id).count()
        temp['total_audits'] = audit_count
        temp["audited_bags"] = db.session.query(disttobag).filter(and_(disttobag.dist_id==dist.id, disttobag.status=="audited")).count()
        temp["picked_bags"] = db.session.query(disttobag).filter(and_(disttobag.dist_id==dist.id, disttobag.status=="picked")).count()
        dist_table_data.append(temp)
    # ---

    # arranging data for depot regional wise

    depo_data = depovendor.query.filter_by(region_name='west').all()
    depo_table_data = []
    for depo in depo_data:
        temp = {}
        temp['name'] = depo.vendor_name
        temp["collected_bags"] = db.session.query(depoinventory).filter(and_(depoinventory.status=="collected",depoinventory.depo_id==depo.id)).count()
        temp["dispatched_bags"] = db.session.query(depoinventory).filter(and_(depoinventory.status=="dispatched",depoinventory.depo_id==depo.id)).count()
        depo_table_data.append(temp)


    # ----

    # arranging data for pickup distributor regional wise
    dist_data = distvendor.query.filter_by(region_name='west').all()
    pickup_table_data = []
    for dist in dist_data:
        temp = {}
        temp["name"] = dist.vendor_name
        temp["total_pickup"] = pickup.query.filter_by(dist_id=dist.id).count()
        temp["picked_bags"] = db.session.query(disttobag).filter(and_(disttobag.dist_id==dist.id, disttobag.status=="picked")).count()
        pickup_table_data.append(temp)

    # ----

    # arranging data for destruction centre region wise
    
    dest_data = destructionvendor.query.filter_by(region_name='west').all()
    dest_table_data = []
    for dest in dest_data:
        temp = {}
        temp['name'] = dest.vendor_name
        temp["collected_bags"] = db.session.query(destructioninventory).filter(and_(destructioninventory.status=="received",destructioninventory.destruction_id==dest.id)).count()
        dest_table_data.append(temp)
    
    # ----
    bar_values= get_deviated_bag_count()
    total_deviated_bag_count = sum(bar_values)
    pie_chart_labels = ['West', 'East', 'South', 'North']
    pie_chart_bag_counts = get_audit_region()
    # raise ValueError(pie_chart_bag_counts)
    total_pie_chart_bag_counts = sum(pie_chart_bag_counts)
    return render_template('general-analysis.html', title='Bitcoin Monthly Price in USD', max=500, set=zip(pie_chart_bag_counts, pie_chart_labels, colors)
            ,pie_chart_bag_counts=total_pie_chart_bag_counts,bar_labels=bar_labels,bar_values=bar_values,
            total_deviated_bag_count=total_deviated_bag_count, dist_table_data=dist_table_data,
            depo_table_data=depo_table_data, pickup_table_data=pickup_table_data,dest_table_data=dest_table_data)




@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith( '.html' ):
            template += '.html'

        return render_template( template )

    except TemplateNotFound:
        return render_template('page-404.html'), 404
    
    except:
        return render_template('page-500.html'), 500
