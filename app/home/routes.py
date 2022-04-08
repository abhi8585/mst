# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from app.home import blueprint
from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app import login_manager
from jinja2 import TemplateNotFound
from app.models import userinfo, usertorole, role
from app.models import depovendor, depotomaster, depotopicker, bag, deviateddepobag, deviateddestructionbag,deviateddepopickbag
from app.models import deviatedbag, role, transportvendor, userinfo, usertorole, auditvendor, auditortovendor, distvendor, disttovendor, sku, transportvendor, transtovendor


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

@blueprint.route('/index')
@login_required
def index():
    
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
