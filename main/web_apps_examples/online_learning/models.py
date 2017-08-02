# from datetime import datetime
# import dbconfig
#
#
# from app import db
#
# from flask_sqlalchemy import SQLAlchemy
#
#
# class videos(db.Model):
#     __bind_key__ = 'project_online_learning_db'
#     __tablename__ = 'videos'
#
#     fields=['id','link']
#     id = db.Column(db.Integer, primary_key=True)
#     link = db.Column(db.text,default='#')
#
#     def __init__(self, ldap_name=""):
#         self.ldap_name = ldap_name
#
#     def __repr__(self):
#         return '<td>{}</td><td>{}</td>'\
#             .format(self.id,self.link)
#
#
# class tags(db.Model):
#     __bind_key__ = 'project_online_learning_db'
#     __tablename__ = 'tags'
#
#     fields=['id','tag']
#     id = db.Column(db.Integer, primary_key=True)
#     tag = db.Column(db.string(100),default='')
#
#     def __init__(self, ldap_name=""):
#         self.ldap_name = ldap_name
#
#     def __repr__(self):
#         return '<td>{}</td><td>{}</td>'\
#             .format(self.id,self.tag)
#
#
# class topic(db.Model):
#     __bind_key__ = 'project_online_learning_db'
#     __tablename__ = 'tags'
#
#     fields=['id','topic']
#     id = db.Column(db.Integer, primary_key=True)
#     topic = db.Column(db.string(100),default='')
#
#     def __init__(self, ldap_name=""):
#         self.ldap_name = ldap_name
#
#     def __repr__(self):
#         return '<td>{}</td><td>{}</td>'\
#             .format(self.id,self.topic)
#
#
# class pages(db.Model):
#     __bind_key__ = 'project_online_learning_db'
#     __tablename__ = 'pages'
#
#     fields=['id','title','text','topic_id']
#     id = db.Column(db.Integer, primary_key=True)
#     text = db.Column(db.text,default='No body')
#     title = db.Column(db.string(100),default='No title')
#     topic_id = db.Column(db.Integer,db.ForeignKey('videos.id'))
#
#
#     def __init__(self, ldap_name=""):
#         self.ldap_name = ldap_name
#
#     def __repr__(self):
#         return '<td>{}</td><td>{}</td><td>{}</td>'\
#             .format(self.id,self.title,self.text[:100],self.topic_id)
#
#
# class pages_videos():
#     __bind_key__ = 'project_online_learning_db'
#     __tablename__ = 'pages_videos'
#
#     fields=['id','video_id','page_id']
#     id = db.Column(db.Integer, primary_key=True)
#     video_id = db.Column(db.Integer,db.ForeignKey('videos.id'))
#     page_id = db.Column(db.Integer,db.ForeignKey('pages.id'))
#
#     def __init__(self, ldap_name=""):
#         self.ldap_name = ldap_name
#
#     def __repr__(self):
#         return '<td>{}</td><td>{}</td><td>{}</td>'\
#             .format(self.id,self.video_id,self.page_id)
#
#
# class pages_tags():
#     __bind_key__ = 'project_online_learning_db'
#     __tablename__ = 'pages_tags'
#
#     fields=['id','page_id','tag_id']
#     id = db.Column(db.Integer, primary_key=True)
#     page_id = db.Column(db.Integer,db.ForeignKey('pages.id'))
#     tag_id = db.Column(db.Integer,db.ForeignKey('tags.id'))
#
#     def __init__(self, ldap_name=""):
#         self.ldap_name = ldap_name
#
#     def __repr__(self):
#         return '<td>{}</td><td>{}</td><td>{}</td>'\
#             .format(self.id,self.page_id, self.tag_id)
