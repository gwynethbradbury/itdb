from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

iaas_home = Blueprint('iaas_home', __name__,
                        template_folder='templates',static_folder='static')

@iaas_home.route('/', defaults={'page': 'index'})
@iaas_home.route('/<page>')
def show(page):
    try:
        return render_template('%s.html' % page)
    except TemplateNotFound:
        abort(404)
