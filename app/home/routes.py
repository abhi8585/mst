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

@blueprint.route('/index')
@login_required
def index():
    role_mapping = {
        "master" : [{"name":"Dashboard","icon":"nav-icon fas fa-tachometer-alt","href":"home_blueprint.index"},
                    {"name":"Create Auditor","icon":"nav-icon fas fa-th","href":"pack_blueprint.listauditor"}
                    # {"name":"Dashboard","icon":"nav-icon fas fa-tachometer-alt","href":"url_for('home_blueprint.index')"}
                    ],
        "Distributor Master" : [{"name":"Create Distributor","icon":"nav-icon fas fa-tachometer-alt","href":"home_blueprint.index"},
                    # {"name":"Create Auditor","icon":"nav-icon fas fa-th","href":"pack_blueprint.listauditor"}
                    # {"name":"Dashboard","icon":"nav-icon fas fa-tachometer-alt","href":"url_for('home_blueprint.index')"}
                    ]
        }
    # user_id = userinfo.query.filter_by(email=current_user.email).first()
    # role_id = usertorole.query.filter_by(user_id=user_id.id).first()
    # role_name = role.query.filter_by(id=role_id.role_id).first()
    # role_permissions = role_mapping[role_name.name]
    return render_template('index3.html')

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
