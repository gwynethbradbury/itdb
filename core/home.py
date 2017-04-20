from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

home = Blueprint('home', __name__,template_folder='templates')#,
                 # static_folder='core/static')


@home.route('/', defaults={'page': 'index'})
@home.route('/<page>')
def show(page):
    try:
        return render_template('%s.html' % page)
    except TemplateNotFound:
        abort(404)


@home.route('/dbas')
def dbas():
    instances = []
    try:
        instances.append('map')
        instances.append('another app')
    except Exception as e:
        print e
    for inst in instances:
        print(inst)
    return render_template("index.html", instances=instances)
