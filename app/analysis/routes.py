from datetime import date, datetime
from email import message
# from sys import audit
from app.analysis import blueprint
from app.models import auditsku, audittobag, deviatedbag, picktobag, pickup, role, transportvendor, userinfo, usertorole, auditvendor, auditortovendor, distvendor, disttovendor, sku, transportvendor, transtovendor
from .. import db
from decouple import config
import json, requests
from flask import jsonify, render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response
# import pdfkit
import os
from app.base.util import hash_pass
from app.base.models import User
# from flask_restful import Resource, Api
from app.models import depovendor, depotomaster, depotopicker, bag, deviateddepobag, deviateddestructionbag,deviateddepopickbag, audit





# labels = [
#     'JAN', 'FEB', 'MAR', 'APR',
#     'MAY', 'JUN', 'JUL', 'AUG',
#     'SEP', 'OCT', 'NOV', 'DEC'
# ]

values = [
    800, 400, 200, 100, 50
]

colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]


def get_bag_count():
    bag_count = []
    bag_status = ['audited', 'picked', 'collected', 'dispatched', 'received']
    for temp in bag_status:
        temp_bag_count = bag.query.filter_by(status=temp).count()
        bag_count.append(temp_bag_count)
    return bag_count





def get_deviated_bag_count():
    bag_count = []
    bag_count.append(deviatedbag.query.count())
    bag_count.append(deviateddepobag.query.count())
    bag_count.append(deviateddepopickbag.query.count())
    bag_count.append(deviateddestructionbag.query.count())
    return bag_count

@blueprint.route('/general')
def general():
    bar_labels=[
    'Transporter', 'Depo Master', 'Depo picker', 'Destruction Master'
]



    bar_values= get_deviated_bag_count()
    total_deviated_bag_count = sum(bar_values)
    pie_chart_labels = ['Audited', 'Picked', 'Collected', 'Dispathched', 'Received']
    pie_chart_bag_counts = get_bag_count()
    total_pie_chart_bag_counts = sum(pie_chart_bag_counts)
    return render_template('general-analysis.html', title='Bitcoin Monthly Price in USD', max=500, set=zip(pie_chart_bag_counts, pie_chart_labels, colors)
            ,pie_chart_bag_counts=total_pie_chart_bag_counts,bar_labels=bar_labels,bar_values=bar_values,
            total_deviated_bag_count=total_deviated_bag_count)



@blueprint.route('/auditanalysis')
def auditanalysis():
    bar_labels=[
    'Transporter', 'Depo Master', 'Depo picker', 'Destruction Master'
]

    # total number of audits

    pie_chart_values = []
    total_audit_count = audit.query.count()
    total_audit_bag_count = audittobag.query.count()
    total_audit_sku_count = auditsku.query.count()
    # raise ValueError(total_audit_sku_count)

    bar_values= get_deviated_bag_count()
    total_deviated_bag_count = sum(bar_values)
    pie_chart_labels = ['Total Audits', 'Total Audited Bag', 'Total Audited SKU', 'Total Overweight Bags', 'Total Underweight Bags']
    pie_chart_bag_counts = get_bag_count()
    total_pie_chart_bag_counts = sum(pie_chart_bag_counts)
    return render_template('audit-analysis.html', title='Bitcoin Monthly Price in USD', max=500, set=zip(pie_chart_bag_counts, pie_chart_labels, colors)
            ,pie_chart_bag_counts=total_pie_chart_bag_counts,bar_labels=bar_labels,bar_values=bar_values,
            total_deviated_bag_count=total_deviated_bag_count)

# for transporter
def get_pickup_pie_chart_data():
    pickup_count = []
    pickup_count.append(pickup.query.count())
    pickup_count.append(pickup.query.filter_by(status="collected").count())
    return pickup_count

        
# for transporter
def get_pick_bag_data():
    data = db.session.query(bag).join(picktobag, picktobag.bag_id == bag.id, isouter=True).count()
    raise ValueError(data)

@blueprint.route('/transportanalysis')
def transportanalysis():
    bar_labels=[
    'Transporter', 'Depo Master', 'Depo picker', 'Destruction Master'
]

    # total number of audits

    pie_chart_values = []
    total_audit_count = audit.query.count()
    total_audit_bag_count = audittobag.query.count()
    total_audit_sku_count = auditsku.query.count()
    # raise ValueError(total_audit_sku_count)

    bar_values= get_deviated_bag_count()
    total_deviated_bag_count = sum(bar_values)
    pie_chart_labels = ['Total Pickups', 'Total Completed Pickups']
    pie_chart_bag_counts = get_pickup_pie_chart_data()
    total_pie_chart_bag_counts = pie_chart_bag_counts[0]
    return render_template('transporter-analysis.html', title='Bitcoin Monthly Price in USD', max=500, set=zip(pie_chart_bag_counts, pie_chart_labels, colors)
            ,pie_chart_bag_counts=total_pie_chart_bag_counts,bar_labels=bar_labels,bar_values=bar_values,
            total_deviated_bag_count=total_deviated_bag_count)