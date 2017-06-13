from flask import Blueprint, abort
from jinja2 import TemplateNotFound

import dbconfig
from flask import request, session, flash, redirect, url_for, render_template
from .email import send_email_simple as send_email

import iaasldap

if dbconfig.test:
    from mock_access_helper import MockAccessHelper as AccessHelper
else:
    from access_helper import AccessHelper
AH = AccessHelper()

home = Blueprint('home', __name__,template_folder='templates')#,
                 # static_folder='core/static')


dbas = 1
nc = 2
iam = 3

@home.route('/')#, defaults={'page': 'index'})
def get_all_dbas_projects():
    try:
        instances = AH.get_projects(dbas)
        return render_template("index.html",
                               username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                               servicelist=iaasldap.get_groups(iaasldap.uid_trim()),
                               instances=instances)
    except TemplateNotFound:
        abort(404)

@home.route('/<page>')
def show(page):
    try:
        instances = AH.get_projects(dbas)
        return render_template("%s.html" % page,
                               username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                               servicelist=iaasldap.get_groups(iaasldap.uid_trim()))
    except TemplateNotFound:
        abort(404)


@home.route('/group/<group>')
def projects_by_group(group):
    instances = AH.get_projects_for_group(group)
    return render_template("groupprojects.html",
                           username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                           servicelist=iaasldap.get_groups(iaasldap.uid_trim()),
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
