from datetime import datetime
import dbconfig

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, Time, text,Boolean
from sqlalchemy.orm import relationship
# from sqlalchemy.ext.declarative import declarative_base
# from main.sqla.app import db
import pymysql

from main.web_apps_examples.online_learning import onlinelearningdb as db

from flask_sqlalchemy import SQLAlchemy


Base = db.Model
metadata = Base.metadata

class video(db.Model):
    __bind_key__ = 'online_learning'
    __tablename__ = 'video'

    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.Text,default='#')

    page_id = Column(ForeignKey(u'page.id'), nullable=False, index=True)
    page_inst = relationship(u'page', back_populates=u'videos')

    def __init__(self, page_inst, link=""):
        self.link = link
        self.page_inst=page_inst

    def __repr__(self):
        return self.link


class tag(db.Model):
    __bind_key__ = 'online_learning'
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(100),default='')

    page_id = Column(ForeignKey(u'page.id'), nullable=True, index=True)
    page_inst = relationship(u'page', back_populates=u'tags')

    def __init__(self,tag="tag"):
        self.tag=tag

    def __repr__(self):
        return self.tag


class topic(db.Model):
    __bind_key__ = 'online_learning'
    __tablename__ = 'topic'

    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(100),default='')

    page_id = Column(ForeignKey(u'page.id'), nullable=True, index=True)
    page_inst = relationship(u'page', back_populates=u'topics')

    def __init__(self,topic="topic"):
        self.topic = topic

    def __repr__(self):
        return self.topic

class comment(db.Model):
    __tablename__ = 'comment'
    __bind_key__ = 'online_learning'
    __display_name__ = 'Comment'
    id = Column(Integer, primary_key=True)
    username = Column(String(20))
    comment = Column(Text)
    visible = Column(Boolean)
    created_on = Column(DateTime)

    page_id = Column(ForeignKey(u'page.id'), nullable=False, index=True)
    page_inst = relationship(u'page', back_populates=u'comments')

    def __init__(self,username="user",comment="comment",visible=False,created_on=datetime.utcnow(),page_inst=None):
        self.username=username
        self.comment=comment
        self.visible=visible
        self.created_on=created_on
        self.page_inst=page_inst

    def __str__(self):
        return self.news.title

    def __repr__(self):
        return self.__str__()


class page(db.Model):
    __bind_key__ = 'online_learning'
    __tablename__ = 'page'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text,default='No body')
    title = db.Column(db.String(100),default='No title')


    videos=relationship(u'video', back_populates=u'page_inst')
    topics=relationship(u'topic', back_populates=u'page_inst')
    tags=relationship(u'tag', back_populates=u'page_inst')
    comments=relationship(u'comment', back_populates=u'page_inst')

    def __init__(self, text="body",title="unnamed"):
        self.text = text
        self.title=title

    def __repr__(self):
        return self.title

