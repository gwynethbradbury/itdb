# from ...sqla.app import app as map
# from .models import pages


# from . import uploadfolder

import dbconfig
if dbconfig.test:
    from mockdbhelper import MockDBHelper as DBHelper
else:
    from dbhelper import DBHelper

from main.sqla.dev import *
from main.auth.iaasldap import LDAPUser as iaasldap
iaasldap = iaasldap()
import models


def assignroutes(application, root, db_uri):
    approute = root
    shortapproute = "/online_learning/"
    templateroute = "online_learning/"


    DB = DBHelper()

    @application.route(approute)
    @application.route(shortapproute)
    def onlinelearninghome():
        projects = []
        try:
            pages,topics,tags = DB.getAllPages()
            # projects = DB.get_all_projects()
            # projects = json.dumps(projects)
            return render_template(templateroute+"index"+".html",
                                   pages=pages,topics=topics,tags=tags)#,
                               # username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                               # servicelist=iaasldap.get_groups())
        except Exception as e:
            print e
            data = []
        print(data)
        return render_template(templateroute+"index"+".html",
                               instances=projects,
                               username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                               servicelist=iaasldap.get_groups())

    @application.route(approute + "topics")
    @application.route(shortapproute + "topics")
    def list_topics():
        topics = DB.getTopics()

        return render_template(templateroute+"topic.html",
                               topics=topics)

    @application.route(approute + "topics/<topic_id>")
    @application.route(shortapproute + "topics/<topic_id>")
    def list_pages_in_this_topic(topic_id):
        pages, tags, videos = DB.getTopicResources(topic_id)
        topic = models.Topic.query.filter_by(id=topic_id).first()
        return render_template(templateroute+"topic.html",
                               topic=topic,
                               videos=videos,
                               pages=pages,
                               tags=tags)

    @application.route(approute + "article/<page_id>")
    @application.route(shortapproute + "article/<page_id>")
    def show_article(page_id):
        article = DB.getArticle(page_id)

        return render_template(templateroute+"article.html",
                               article=article)

    @application.route(approute + "tags")
    @application.route(shortapproute + "tags")
    def list_tags():
        tags = DB.getTags()

        return render_template(templateroute+"tag.html",
                               tags=tags)

    @application.route(approute + "tags/<tag>")
    @application.route(shortapproute + "tags/<tag>")
    def list_pages_with_this_tag(tag):
        pages, videos, topics = DB.getTagResources(tag)

        tag = models.Tag.query.filter_by(id=tag).first()

        return render_template(templateroute+"tag.html",
                               tag=tag,
                               videos=videos,
                               pages=pages,
                               tags=[],
                               topics=topics)
