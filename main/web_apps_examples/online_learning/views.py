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


def assignroutes(application):
    approute = "/projects/online_learning/app/"
    shortapproute = "/online_learning/"
    templateroute = "online_learning/"

    dbbb = 'mysql+pymysql://{}:{}@localhost/{}'.format(dbconfig.db_user,
                                                       dbconfig.db_password,
                                                       'online_learning')#map.name)
    # db2 = dataset.connect(dbbb, row_type=pages)
    dbbindkey="project_online_learning_db"
    appname="online_learning"
    DBA = DatabaseAssistant(dbbb,dbbindkey,appname)

    projects = []

    DB = DBHelper("online_learning")#map.name)

    @application.route(approute)
    @application.route(shortapproute)
    def onlinelearninghome():
        projects = []
        try:
            pages,topics,tags = DB.getAllPages()
            # projects = DB.get_all_projects()
            # projects = json.dumps(projects)
            return render_template(templateroute+"index"+".html",
                                   instances=pages,topics=topics,tags=tags,
                               username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                               servicelist=iaasldap.get_groups())
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
                               topics=topics,
                               instances=projects,
                               username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                               servicelist=iaasldap.get_groups())

    @application.route(approute + "topics/<topic>")
    @application.route(shortapproute + "topics/<topic>")
    def list_pages_in_this_topic(topic):
        pages, tags, videos = DB.getTopicResources(topic)


        return render_template(templateroute+"topic.html",
                               topic=topic,
                               videos=videos,
                               pages=pages,
                               tags=tags,
                               instances=projects,
                               username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                               servicelist=iaasldap.get_groups())

    @application.route(approute + "article/<page_id>")
    @application.route(shortapproute + "article/<page_id>")
    def show_article(page_id):
        article,topic,tags = DB.getArticle(page_id)

        return render_template(templateroute+"article.html",
                               article=article,
                               topic=topic,
                               tags=tags,
                               instances=projects,
                               username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                               servicelist=iaasldap.get_groups())

    @application.route(approute + "tags")
    @application.route(shortapproute + "tags")
    def list_tags():
        tags = DB.getTags()

        return render_template(templateroute+"tag.html",
                               tags=tags,
                               instances=projects,
                               username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                               servicelist=iaasldap.get_groups())

    @application.route(approute + "tags/<tag>")
    @application.route(shortapproute + "tags/<tag>")
    def list_pages_with_this_tag(tag):
        pages, tags, videos, topics = DB.getTagResources(tag)

        tag = [DB.getTagName(tag),tag]

        return render_template(templateroute+"tag.html",
                               tag=tag,
                               videos=videos,
                               pages=pages,
                               tags=tags,
                               topics=topics,
                               instances=projects,
                               username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                               servicelist=iaasldap.get_groups())

    # @application.route(approute+"showpoints")
    # def showpoints():
    #     projects = []
    #     try:
    #         data = DB.getallpoints()
    #         print(data)
    #         projects = DB.get_all_projects()
    #         projects = json.dumps(projects)
    #     except Exception as e:
    #         print e
    #         data = []
    #     print(data)
    #     return render_template(templateroute+"map"+".html",
    #                            projects=projects, data=data)
    #
    # @application.route(approute+"submitproject", methods=['GET', 'POST'])
    # def submit():
    #     try:
    #         category = request.form.get("category")
    #         startdate = request.form.get("startdate")
    #         enddate = request.form.get("enddate")
    #         latitude = float(request.form.get("latitude"))
    #         longitude = float(request.form.get("longitude"))
    #         description = request.form.get("description")
    #         DB.add_project(latitude, longitude, startdate, enddate, category, description)
    #     except Exception as e:
    #         print e
    #     # home()
    #     return redirect(approute+"showpoints")#url_for("map"+"_app."+"map"))
    #
    # @application.route(approute+"uploadxls", methods=['GET', 'POST'])
    # def uploadxls():
    #     try:
    #         filename = request.form.get("filename")
    #         DB.uploadxls(filename)
    #     except Exception as e:
    #         print e
    #     return redirect(approute+"showpoints")#redirect(url_for('map_app.map'))

