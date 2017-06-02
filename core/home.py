from flask import Blueprint, abort
from jinja2 import TemplateNotFound

import dbconfig
from flask import request, session, flash, redirect, url_for, render_template
from .email import send_email_simple as send_email


if dbconfig.test:
    from mock_access_helper import MockAccessHelper as AccessHelper
else:
    from access_helper import AccessHelper
AH = AccessHelper()

home = Blueprint('home', __name__,template_folder='templates')#,
                 # static_folder='core/static')


@home.route('/', defaults={'page': 'index'})
@home.route('/<page>')
def show(page):
    try:
        return render_template('%s.html' % page)
    except TemplateNotFound:
        abort(404)

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
