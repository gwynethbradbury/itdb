from datetime import datetime
import dbconfig


from main.sqla.app import db

from flask_sqlalchemy import SQLAlchemy


class item(db.Model):
    __bind_key__ = 'project_it_lending_log_db'
    __tablename__ = 'videos'

    fields=['id','name','comment']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),default='#')
    name = db.Column(db.text,default='#')

    def __init__(self, ldap_name=""):
        self.ldap_name = ldap_name

    def __repr__(self):
        return '<td>{}</td><td>{}</td><td>{}</td>'\
            .format(self.id,self.name,self.comment)



class log(db.Model):
    __bind_key__ = 'project_it_lending_log_db'
    __tablename__ = 'log'

    fields=['id','item','date_out','returned','borrower','signed_out_by','comment']
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.Integer,db.ForeignKey('item.id'))
    date_out = db.Column(db.DateTime,default='datetime.utcnow')
    returned = db.Column(db.Boolean,default='False')
    borrower = db.Column(db.String(100),default='')
    signed_out_by = db.Column(db.String(100),default='')
    comment = db.Column(db.Text,default="")


    def __init__(self, ldap_name=""):
        self.ldap_name = ldap_name

    def __repr__(self):
        return '<td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td>'\
            .format(self.id,self.item,self.date_out,self.returned,self.borrower,self.comment[:100])
