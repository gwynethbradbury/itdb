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



class Video(db.Model):
    __bind_key__ = 'online_learning'
    # __tablename__ = 'Video'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text,default='#', nullable=True)


    page_inst_id = Column(ForeignKey(u'article.id'), nullable=True, index=True)
    page_inst = relationship(u'Article', back_populates=u'videos')

    def __init__(self, page_inst, link=""):
        self.name = link
        self.page_inst_id=page_inst.id

    def __repr__(self):
        return self.name


class Tag(db.Model):
    __bind_key__ = 'online_learning'
    # __tablename__ = 'Tag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),default='')

    def __init__(self,name="tag"):
        self.name=name

    def __repr__(self):
        return self.name


class Topic(db.Model):
    __bind_key__ = 'online_learning'
    # __tablename__ = 'Topic'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),default='')

    def __init__(self,topic="topic"):
        self.name = topic

    def __repr__(self):
        return self.name


class PageTag(db.Model):
    __bind_key__ = 'online_learning'
    # __tablename__ = 'PageTag'
    id = db.Column(db.Integer, primary_key=True)
    tag_id = Column(Integer,ForeignKey(u'tag.id'))
    page_id = Column(Integer, ForeignKey(u'article.id'))

    def __init__(self,tag_id,page_id):
        self.tag_id = tag_id
        self.page_id = page_id

class PageTopic(db.Model):
    __bind_key__ = 'online_learning'
    # __tablename__ = 'PageTopic'
    id = db.Column(db.Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey(u'topic.id'))
    page_id = Column(Integer, ForeignKey(u'article.id'))
#
    def __init__(self,topic_id,page_id):
        self.topic_id = topic_id
        self.page_id = page_id

# class PageVideo(db.Model):
#     __bind_key__ = 'online_learning'
#     __tablename__ = 'PageVideo'
#     id = db.Column(db.Integer, primary_key=True)
#     # vid_id = Column(Integer, ForeignKey(u'Video.id'))
#     # page_id = Column(Integer, ForeignKey(u'Page.id'))
# #
#     def __init__(self,vid_id,page_id):
#         self.vid_id = vid_id
#         self.page_id = page_id




class Comment(db.Model):
    # __tablename__ = 'Comment'
    __bind_key__ = 'online_learning'

    id = Column(Integer, primary_key=True)
    username = Column(String(20))
    title = Column(String(100))
    comment = Column(Text)
    visible = Column(Boolean)
    created_on = Column(DateTime)

    page_inst_id = Column(ForeignKey(u'article.id'), nullable=True, index=True)
    page_inst = relationship(u'Article', back_populates=u'comments')


    def __init__(self,page_inst,username="user",comment="comment",
                 visible=False,created_on=datetime.utcnow()):
        self.username=username
        self.comment=comment
        self.visible=visible
        self.created_on=created_on
        self.page_inst_id=page_inst.id

    def __str__(self):
        return self.news.title

    def __repr__(self):
        return self.__str__()


class Article(db.Model):
    __bind_key__ = 'online_learning'
    # __tablename__ = 'Page'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text,default='No body')
    title = db.Column(db.String(100),default='No title')


    topics=relationship(u"Topic",
                        secondary=PageTopic.__table__,
                        backref=u"pagestopics", lazy='dynamic')
    tags=relationship(u"Tag",
                        secondary=PageTag.__table__,
                        backref=u"pagestags", lazy='dynamic')

    comments=db.relationship(u'Comment', back_populates=u'page_inst', lazy='dynamic')
    videos=db.relationship(u'Video', back_populates=u'page_inst', lazy='dynamic')

    def __init__(self, text="body",title="unnamed"):
        self.text = text
        self.title=title

    def __repr__(self):
        return self.title

