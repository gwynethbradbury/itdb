from datetime import datetime

from .. import db


# | groups          |
# | services        |
# | svc_instances  |


class groups(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ldap_name = db.Column(db.String(60), unique=True)

    def __init__(self, ldap_name=""):
        self.ldap_name = ldap_name

    def __repr__(self):
        return '<ldap_name - {}>'.format(self.ldap_name)


class services(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)

    def __init__(self, name=""):
        self.name = name

    def __repr__(self):
        return '<name - {}>'.format(self.name)


class svc_instances(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    identifier = db.Column(db.String(60), unique=True)
    svc_type_id = db.Column(db.Integer, db.ForeignKey('services.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))

    def __init__(self, name="", identifier="",svc_type_id=0,group_id=0):
        self.name = name
        self.identifier=identifier
        self.svc_type_id=svc_type_id
        self.group_id=group_id

    def __repr__(self):
        return '<name - {}, description - {}, type - {}, group - {}>'.format(self.name,self.identifier,self.svc_type_id,self.group_id)


class permitted_svc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    svc_id = db.Column(db.Integer, db.ForeignKey('services.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))

    def __init__(self, name="", identifier="",svc_type_id=0,group_id=0):
        self.svc_id=svc_type_id
        self.group_id=group_id

    def __repr__(self):
        return '<service - {}, group - {}>'.format(self.svc_id,self.group_id)






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
