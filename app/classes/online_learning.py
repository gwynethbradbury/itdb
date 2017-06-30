# coding: utf-8
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base


from . import database as db
Base = db.Model
metadata = Base.metadata


class Pages(Base):
    def __str__(self):
        return self.text
    __tablename__ = 'pages'

    id = Column(Integer, primary_key=True)
    text = Column(Text)
    title = Column(String(100))
    topic_id = Column(Integer)


class PagesTags(Base):
    def __str__(self):
        return self.page_id
    __tablename__ = 'pages_tags'

    id = Column(Integer, primary_key=True)
    page_id = Column(Integer)
    tag_id = Column(Integer)


class PagesVideos(Base):
    def __str__(self):
        return self.video_id
    __tablename__ = 'pages_videos'

    id = Column(Integer, primary_key=True)
    video_id = Column(Integer)
    page_id = Column(Integer)


class Tags(Base):
    def __str__(self):
        return self.tag
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    tag = Column(String(100))


class Topic(Base):
    def __str__(self):
        return self.topic
    __tablename__ = 'topic'

    id = Column(Integer, primary_key=True)
    topic = Column(String(100))
    description = Column(Text)


class Videos(Base):
    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True)
    link = Column(String(100))
