# admin.py

from flask import Blueprint, request, g, redirect, url_for, abort, \
    render_template

from flask.views import MethodView
from wtforms.ext.sqlalchemy.orm import model_form

from app import db

from .models import news, iaas_events, subscribers, comment, services, groups, permitted_svc, svc_instances
from .. import iaasldap

admin = Blueprint('admin', __name__)

class CRUDView(MethodView):
    list_template = 'admin/listview.html'
    detail_template = 'admin/detailview.html'

    def __init__(self, model, endpoint, list_template=None,
                 detail_template=None, exclude=None, filters=None):
        self.model = model
        self.endpoint = endpoint
        # so we can generate a url relevant to this
        # endpoint, for example if we utilize this CRUD object
        # to enpoint comments the path generated will be
        # /admin/comments/
        self.path = url_for('.%s' % self.endpoint)
        if list_template:
            self.list_template = list_template
        if detail_template:
            self.detail_template = detail_template
        self.filters = filters or {}
        self.ObjForm = model_form(self.model, db.session, exclude=exclude)

    def render_detail(self, **kwargs):
        usersgroups = iaasldap.get_groups(iaasldap.uid_trim())
        if "superusers" in usersgroups:
            return render_template(self.detail_template, path=self.path,
                                   username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                                   servicelist=iaasldap.get_groups(iaasldap.uid_trim()),
                                   **kwargs)
        else:
            return abort(401)

    def render_list(self, **kwargs):
        usersgroups = iaasldap.get_groups(iaasldap.uid_trim())
        if "superusers" in usersgroups:
            return render_template(self.list_template, path=self.path,
                                   filters=self.filters,
                                   username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                                   servicelist=iaasldap.get_groups(iaasldap.uid_trim()),
                                   **kwargs)
        else:
            return abort(401)

    def get(self, obj_id='', operation='', filter_name=''):
        if operation == 'new':
            #  we just want an empty form
            form = self.ObjForm()
            action = self.path
            return self.render_detail(form=form, action=action)

        if operation == 'delete':
            obj = self.model.query.get(obj_id)
            db.session.delete(obj)
            db.session.commit()
            return redirect(self.path)

        # list view with filter
        if operation == 'filter':
            func = self.filters.get(filter_name)
            obj = func(self.model)
            return self.render_list(obj=obj, filter_name=filter_name)

        if obj_id:
            # this creates the form fields base on the model
            # so we don't have to do them one by one
            ObjForm = model_form(self.model, db.session)

            obj = self.model.query.get(obj_id)
            # populate the form with our blog data
            form = self.ObjForm(obj=obj)
            # action is the url that we will later use
            # to do post, the same url with obj_id in this case
            action = request.path
            return self.render_detail(form=form, action=action)

        obj = self.model.query.order_by(self.model.id.desc()).all()
        return self.render_list(obj=obj)

    def post(self, obj_id=''):
        # either load and object to update if obj_id is given
        # else initiate a new object, this will be helpfull
        # when we want to create a new object instead of just
        # editing existing one
        if obj_id:
            obj = self.model.query.get(obj_id)
        else:
            obj = self.model()

        ObjForm = model_form(self.model, db.session)
        # populate the form with the request data
        form = self.ObjForm(request.form)
        # this actually populates the obj (the blog post)
        # from the form, that we have populated from the request post
        form.populate_obj(obj)

        db.session.add(obj)
        db.session.commit()

        return redirect(self.path)


# def dec(f):
#     def decorated(*args, **kwargs):
#         print 'run decorator run'
#         return f(*args, **kwargs)
#     return decorated



import core.iaasldap as iaasldap

def register_crud(app, url, endpoint, model, decorators=[], **kwargs):
    view = CRUDView.as_view(endpoint, endpoint=endpoint,
                            model=model, **kwargs)

    for decorator in decorators:
        view = decorator(view)

    app.add_url_rule('%s/' % url, view_func=view, methods=['GET', 'POST'])
    app.add_url_rule('%s/<int:obj_id>/' % url, view_func=view)
    app.add_url_rule('%s/<operation>/' % url, view_func=view, methods=['GET'])
    app.add_url_rule('%s/<operation>/<int:obj_id>/' % url, view_func=view,
                     methods=['GET'])
    app.add_url_rule('%s/<operation>/<filter_name>/' % url, view_func=view,
                     methods=['GET'])







news_filters = {
    'Created_asc': lambda model: model.query.order_by(model.created_on.asc()).all(),
    'Updated_desc': lambda model: model.query.order_by(model.updated_on.desc()).all(),
    'Last_3': lambda model: model.query.order_by(model.created_on.desc()).all()[:3]
}
iaas_events_filters = {
    'Event_date': lambda model: model.query.order_by(model.eventdate.asc()).all(),
    # 'Past_Events': lambda model:model.query.filter_by(model.eventdate<datetime.utcnow().date()).all(),
    # 'Future_Events': lambda model:model.query.filter_by(eventdate>time).all(),
    'Title': lambda model: model.query.order_by(model.title.asc()).all(),
    # 'Next_3': lambda model: model.query.order_by(model.eventdate.asc()).all()[:1]
}
comment_filters = {
    'Invisible': lambda model: model.query.filter_by(visible=False).all(),
    'Visible': lambda model: model.query.filter_by(visible=True).all()
}

subscriber_filters = {
    'Name': lambda model: model.query.order_by(model.name.asc()).all(),
    'email': lambda model: model.query.order_by(model.email.asc()).all()
}

svc_instance_filters={
    'DBAS':lambda model:model.query.filter_by(svc_type_id=1).all(),
    'Nextcloud':lambda model:model.query.filter_by(svc_type_id=2).all(),
    'IAM':lambda model:model.query.filter_by(svc_type_id=3).all()
}

register_crud(admin, '/news', 'news', news, filters=news_filters)
register_crud(admin, '/iaas_events', 'iaas_events', iaas_events, filters=iaas_events_filters)
register_crud(admin, '/subscribers', 'subscribers', subscribers, filters=subscriber_filters)
register_crud(admin, '/comments', 'comment', comment, filters=comment_filters)
register_crud(admin, '/service_instances', 'service_instances', svc_instances, filters=svc_instance_filters)

register_crud(admin, '/groups', 'groups', groups)
register_crud(admin, '/permitted_svc', 'permitted_svc', permitted_svc)
register_crud(admin, '/services', 'services', services)