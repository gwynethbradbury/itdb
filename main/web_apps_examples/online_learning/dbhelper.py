import pymysql
import dbconfig
from time import time
from datetime import datetime
from numpy import genfromtxt
import json

import models
from .import onlinelearnapp, onlinelearningdb
from flask_sqlalchemy import SQLAlchemy

db = onlinelearningdb


class DBHelper:
    def __init__(self, dbname):
        self.mydatabase = dbname


    def getAllPages(self):
        pages = models.page.query.all()
        topics= models.topic.query.all()
        tags= models.tag.query.all()

        return pages,topics,tags

    def getAllPagesByTag(self,tag_id):
        pagestmp = models.page.query.all()
        pages=[]
        tag = models.tag.query.filter_by(id=tag_id).first()
        for p in pagestmp:
            if tag in p.tags:
                pages.append(p)

        return pages

    def getAllPagesByTopic(self,topic_id):
        pagestmp = models.page.query.all()
        pages=[]
        topic = models.topic.query.filter_by(id=topic_id).first()
        for p in pagestmp:
            if topic in p.topics:
                pages.append(p)

        return pages

    def getTopicsByTag(self,tag_id):
        pagestmp = models.page.query.all()
        topics=[]
        tag = models.tag.query.filter_by(id=tag_id).first()
        for p in pagestmp:
            if tag in p.tags:
                for t in p.topics:
                    topics.append(t)
        return topics
    def getTagsByTopic(self,topic_id):
        pagestmp = models.page.query.all()
        tags=[]
        topic = models.topic.query.filter_by(id=topic_id).first()
        for p in pagestmp:
            if topic in p.topics:
                for t in p.tags:
                    tags.append(t)
        return tags
    def getVideosByTopic(self,topic_id):
        pagestmp = models.page.query.all()
        videos=[]
        topic = models.topic.query.filter_by(id=topic_id).first()
        for p in pagestmp:
            if topic in p.topics:
                for v in p.videos:
                    videos.append(v)
        return videos
    def getVideosByTag(self,tag_id):
        pagestmp = models.page.query.all()
        videos=[]
        tag = models.tag.query.filter_by(id=tag_id).first()
        for p in pagestmp:
            if tag in p.tags:
                for v in p.videos:
                    videos.append(v)
        return videos

    def getTopicResources(self,topic_id):

        pages = self.getAllPagesByTopic(topic_id)

        videos = self.getVideosByTopic(topic_id)

        tags = self.getTagsByTopic(topic_id)

        return pages, tags, videos


    def getTagResources(self,tag_id):

        pages = self.getAllPagesByTag(tag_id)

        videos = self.getVideosByTag(tag_id)

        topics = self.getTopicsByTag(tag_id)


        return pages, videos, topics


    def getArticle(self,page_id):
        return models.page.query.filter_by(id=page_id).first()

    def getTopics(self):
        return models.topic.query.all()

    def getTags(self):
        return models.tag.query.all()
