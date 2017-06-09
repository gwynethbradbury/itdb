from datetime import datetime
from .. import db


# | groups          |
# | services        |
# | svc_instances  |


class groups(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ldap_name = db.Column(db.String(60), unique=True)
    fields=['id','ldap_name']

    def __init__(self, ldap_name=""):
        self.ldap_name = ldap_name

    def __repr__(self):
        return '<td>{}</td><td>{}</td>'.format(self.id,self.ldap_name)


class services(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    fields=['id','name']

    def __init__(self, name=""):
        self.name = name

    def __repr__(self):
        return '<td>{}</td><td>{}</td>'.format(self.id,self.name)


class svc_instances(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_display_name = db.Column(db.String(60), unique=True)
    instance_identifier = db.Column(db.String(60), unique=True)
    svc_type_id = db.Column(db.Integer, db.ForeignKey('services.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    fields=['id','name','identifier','service type ID','group ID']

    def __init__(self, project_display_name="", instance_identifier="",svc_type_id=0,group_id=0):
        self.project_display_name = project_display_name
        self.instance_identifier=instance_identifier
        self.svc_type_id=svc_type_id
        self.group_id=group_id

    def __repr__(self):
        return '<td>{0}</td><td>{1}</td><td><a href="{2}">{2}</a></td><td>{3}</td><td>{4}</td>'.format(self.id,
                                                                                self.project_display_name,
                                                                             self.instance_identifier,
                                                                             self.svc_type_id,
                                                                             self.group_id)


class permitted_svc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    svc_id = db.Column(db.Integer, db.ForeignKey('services.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    fields=['id','service ID','group ID']

    def __init__(self, name="", identifier="",svc_type_id=0,group_id=0):
        self.svc_id=svc_type_id
        self.group_id=group_id

    def __repr__(self):
        return '<td>{}</td><td>{}</td><td>{}</td>'.format(self.id,self.svc_id,self.group_id)






class news(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), unique=True)
    body = db.Column(db.Text())

    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow,
                                          onupdate=datetime.utcnow)
    fields=['title']

    def __init__(self, title="", body=""):
        self.title = title
        self.body = body

    def __repr__(self):
        return '<td>{}</td>'.format(self.title)

class iaas_events(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(60), unique=True)
    subtitle = db.Column(db.String(60), unique=True)
    description = db.Column(db.String(255), unique=True)
    room = db.Column(db.String(60))

    eventdate = db.Column(db.DateTime(), default=datetime.utcnow().date(), unique=True)
    starttime = db.Column(db.DateTime, default=datetime.utcnow().time())
    endtime = db.Column(db.DateTime, default=datetime.utcnow().time())

    fields=['title','subtitle']

    def __init__(self, title="", subtitle="", desc="",room=""):
        self.title = title
        self.subtitle = subtitle
        self.description = desc
        self.room = room

    def __repr__(self):
        return '<td>{}</td><td>{}</td><td>{}</td>'.format(self.title,self.subtitle,self.eventdate)



class subscribers(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(60), unique=True)
    email = db.Column(db.String(60), unique=True)
    fields=['name','email']


    def __init__(self, name="", email=""):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<td>{}</td><td>{}</td>'.format(self.name,self.email)

class comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'))
    news = db.relationship('news', backref=db.backref('comments',
                                                      lazy='dynamic'))

    username = db.Column(db.String(20),default="Anon")
    comment = db.Column(db.Text())
    visible = db.Column(db.Boolean(), default=False)

    created_on = db.Column(db.DateTime(), default=datetime.utcnow)

    fields=['Article','user','comment']

    def __init__(self, post='', username='', comment=''):
        if post:
            self.news = post
        self.username = username
        self.comment = comment

    def __repr__(self):
        return '<td>{}</td><td>{}</td><td>{}</td>'.format(self.news.title, self.comment[:20],self.username)
