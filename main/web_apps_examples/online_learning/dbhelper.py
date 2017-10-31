import pymysql
import dbconfig
from time import time
from datetime import datetime
from numpy import genfromtxt
import json

import models
from .import onlinelearnapp, onlinelearningdb as db
from flask_sqlalchemy import SQLAlchemy



class DBHelper:
    def __init__(self):
        pass

    def getAllPages(self):
        pages = models.Article.query.all()
        topics= models.Topic.query.all()
        tags= models.Tag.query.all()

        return pages,topics,tags



    def getTopicsByTag(self,tag_id):
        pagestmp = models.Article.query.all()
        topics=[]
        tag = models.Tag.query.filter_by(id=tag_id).first()
        for p in pagestmp:
            if tag in p.tags:
                for t in p.topics:
                    topics.append(t)
        return topics
    def getTagsByTopic(self,topic_id):
        pagestmp = models.Article.query.all()
        tags=[]
        topic = models.Topic.query.filter_by(id=topic_id).first()
        for p in pagestmp:
            if topic in p.topics:
                for t in p.tags:
                    tags.append(t)
        return tags
    def getVideosByTopic(self,topic_id):
        pagestmp = models.Article.query.all()
        videos=[]
        topic = models.Topic.query.filter_by(id=topic_id).first()
        for p in pagestmp:
            if topic in p.topics:
                for v in p.videos:
                    videos.append(v)
        return videos
    def getVideosByTag(self,tag_id):
        pagestmp = models.Article.query.all()
        videos=[]
        tag = models.Tag.query.filter_by(id=tag_id).first()
        for p in pagestmp:
            if tag in p.tags:
                for v in p.videos:
                    videos.append(v)
        return videos

    def getTopicResources(self,topic_id):

        # pages = self.getAllPagesByTopic(topic_id)

        videos = self.getVideosByTopic(topic_id)

        # tags = self.getTagsByTopic(topic_id)

        return videos


    def getTagResources(self,tag_id):

        # pages = self.getAllPagesByTag(tag_id)

        videos = self.getVideosByTag(tag_id)

        # topics = self.getTopicsByTag(tag_id)


        return videos


    def getArticle(self,page_id):
        return models.Article.query.filter_by(id=page_id).first()

    def getTopics(self):
        return models.Topic.query.all()

    def getTags(self):
        return models.Tag.query.all()
