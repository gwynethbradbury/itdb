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
        return '<td>{0}</td><td>{1}</td><td><a href="/{2}">{2}</a></td><td>{3}</td><td>{4}</td>'.format(self.id,
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
        return '<td>{}</td><td>{}</td><td>{}</td>'.format(self.svc_id,self.group_id)






class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), unique=True)
    body = db.Column(db.Text())

    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow,
                                          onupdate=datetime.utcnow)

    def __init__(self, title="", body=""):
        self.title = title
        self.body = body

    def __repr__(self):
        return '<Blogpost - {}>'.format(self.title)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'))
    blog = db.relationship('Blog', backref=db.backref('comments',
                                                      lazy='dynamic'))

    username = db.Column(db.String(50))
    comment = db.Column(db.Text())
    visible = db.Column(db.Boolean(), default=False)

    created_on = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, post='', username='', comment=''):
        if post:
            self.blog = post
        self.username = username
        self.comment = comment

    def __repr__(self):
        return '<Comment: blog {}, {}>'.format(self.blog_id, self.comment[:20])
