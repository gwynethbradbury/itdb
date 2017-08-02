#should hold all the routes
from flask import abort
from flask import request, redirect, render_template
from jinja2 import TemplateNotFound

import dbconfig
import iaasldap.LDAPUser as iaasldap
iaasldap = iaasldap()
from home import app as home
from .email import send_email_simple as send_email

if dbconfig.test:
    from mock_access_helper import MockAccessHelper as AccessHelper
else:
    from access_helper import AccessHelper
AH = AccessHelper()


@home.context_processor
def inject_url():
    iaas_url=dbconfig.iaas_route
    dbas_url=dbconfig.dbas_route
    return dict(iaas_url=iaas_url,dbas_url=dbas_url)

@home.route('/')#, defaults={'page': 'index'})
def get_all_dbas_projects():
    try:
        instances = AH.get_projects("dbas")
        return render_template("index.html",
                               username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                               servicelist=iaasldap.get_groups(),
                               instances=instances)
    except TemplateNotFound:
        abort(404)


@home.route('/<page>')
def show(page):
    try:
        return render_template("%s.html" % page,
                               username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                               servicelist=iaasldap.get_groups())
    except TemplateNotFound:
        abort(404)

# def iaas_url():
#     try:
#         return dbconfig.iaas_route
#     except TemplateNotFound:
#         abort(404)


@home.route('/group/<group>')
def projects_by_group(group):
    instances = AH.get_projects_for_group(group)
    return render_template("groupprojects.html",
                           username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                           servicelist=iaasldap.get_groups(),
                           instances=instances, group=group)

@home.route('/sendenquiry', methods=['GET', 'POST'])
def sendenquiry():
    send_email('gwyneth.bradbury@ouce.ox.ac.uk', 'IAAS Enquiry', request.form['messagebody'])
    return redirect('/')

# @home.route('/dbas')
# def dbas():
#     instances = []
#     try:
#         instances.append('map')
#         instances.append('another app')
#     except Exception as e:
#         print e
#     for inst in instances:
#         print(inst)
#     return render_template("index.html", instances=instances)
