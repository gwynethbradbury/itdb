from datetime import datetime
import dbconfig


from app import db

from flask_sqlalchemy import SQLAlchemy




class project(db.Model):
    __bind_key__ = 'project_map_db'
    __tablename__ = 'project'

    id = db.Column(db.Integer, primary_key=True)

    latitude = db.Column(db.Float, default=51.758759)
    longitude = db.Column(db.Float, default=-1.253690)
    startdate = db.Column(db.DateTime, default=datetime.utcnow)
    enddate = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(50),default='')
    description = db.Column(db.String(100),default='')
    updated_at = db.Column(db.DateTime(), default=datetime.utcnow)


    fields=['id','latitude','longitude','startdate','enddate','category','description','updated_at']

    def __init__(self, ldap_name=""):
        self.ldap_name = ldap_name

    def __repr__(self):
        return '<td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td>'\
            .format(self.id,self.latitude,self.longitude,self.startdate,self.enddate,self.category,self.description,self.updated_at)

