import pymysql
import dbconfig
from time import time
from datetime import datetime
from numpy import genfromtxt
import json


class DBHelper:
    def __init__(self, dbname):
        self.mydatabase = dbname

    def connect(self, database=""):
        return pymysql.connect(host='localhost',
                               user=dbconfig.db_user,
                               passwd=dbconfig.db_password,
                               db=self.mydatabase)

    def getAllPages(self,topic_id=""):
        pages = []
        topics=[]
        tags=[]
        try:
            connection = self.connect()
            query = "SELECT name,text,topic_id,id FROM pages"

            if topic_id:
                query=query+" WHERE topic_id={}".format(str(topic_id))

            query=query+";"

            with connection.cursor() as cursor:
                cursor.execute(query)
            for page in cursor:
                article = [page[0], page[1][:300],page[3]]
                pages.append(article)
                _topic,_tags = self.getPageTopicTags(page[3],page[2])
                topics.append(_topic)
                tags.append(_tags)
                print(page[0])
            # pages.reverse()


            return pages,topics,tags
        except Exception as e:
            print(e)
            return pages,topics,tags
        finally:
            connection.close()

    def getAllPagesByTag(self,tag_id):
        page_ids=[]
        try:
            connection = self.connect()

            query = "SELECT page_id FROM pages_tags WHERE tag_id={};".format(str(tag_id))
            with connection.cursor() as cursor:
                cursor.execute(query)
            for page_id in cursor:
                page_ids.append(page_id[0])

            return page_ids

        except Exception as e:
            print(e)
        finally:
            connection.close()

    def getPageTopicTags(self,page_id,topic_id):
        topic="None"
        tags=[]
        try:
            connection = self.connect()
            query = "SELECT topic FROM topic WHERE id={};".format(str(topic_id))
            with connection.cursor() as cursor:
                cursor.execute(query)
            for c in cursor:
                topic = c[0]

            tag_ids=[]
            query = "SELECT tag_id FROM pages_tags WHERE page_id={};".format(str(page_id))
            with connection.cursor() as cursor:
                cursor.execute(query)
            for tag_id in cursor:
                tag_ids.append(tag_id[0])

            for t in tag_ids:
                query = "SELECT tag FROM tags WHERE id={};".format(str(t))
                with connection.cursor() as cursor:
                    cursor.execute(query)
                for c in cursor:
                    tags.append([c[0],t])

            return topic,tags

        except Exception as e:
            print(e)
        finally:
            connection.close()

        return topic,tags

    def getTopicResources(self,topic):
        videos=[]
        pages=[]
        tags=[]

        try:


            connection = self.connect()
            query = "SELECT id FROM topic WHERE topic='{}';".format(topic)
            with connection.cursor() as cursor:
                cursor.execute(query)
            for c in cursor:
                topic_id = c[0]
            pages, topics, tags = self.getAllPages(topic_id)

            videos = self.getVideosForTopic(topic_id)

            return pages, tags, videos


        except Exception as e:
            print(e)
        finally:
            connection.close()

        return pages, tags, videos

    def getTagName(self,tag_id):
        tag="Undefined tag"

        try:


            connection = self.connect()
            query = "SELECT tag FROM tags WHERE id='{}';".format(tag_id)
            with connection.cursor() as cursor:
                cursor.execute(query)
            for c in cursor:
                tag = c[0]

            return tag



        except Exception as e:
            print(e)
        finally:
            connection.close()

        return tag
    def getTagResources(self,tag_id):
        videos=[]
        pages=[]
        tags=[]
        topics=[]

        try:


            # connection = self.connect()
            # query = "SELECT id FROM tags WHERE tag='{}';".format(tag)
            # with connection.cursor() as cursor:
            #     cursor.execute(query)
            # for c in cursor:
            #     tag_id = c[0]
            page_ids = self.getAllPagesByTag(tag_id)

            for p in page_ids:
                page, _topic, _tags = self.getArticle(p)
                pages.append(page)
                # _topics, _tags = self.getPageTopicTags(p)
                tags.append(_tags)
                topics.append(_topic)
                v = self.getVideosForPage(p)
                for i in v:
                    videos.append(i)

            return pages, tags, videos, topics


        except Exception as e:
            print(e)
        # finally:
        #     connection.close()

        return pages, tags, videos, topics

    def getVideosForTopic(self,topic_id):
        videos=[]
        page_ids=[]
        # get pages under topic, for each page get page videos
        try:

            connection = self.connect()
            query = "SELECT id FROM pages WHERE topic_id='{}';".format(topic_id)
            with connection.cursor() as cursor:
                cursor.execute(query)
            for c in cursor:
                page_ids.append(c[0])


        except Exception as e:
            print(e)
        finally:
            connection.close()

        for p in page_ids:
            videosperpage = self.getVideosForPage(p)
            for v in videosperpage:
                videos.append(v)
        return videos

    def getArticle(self,page_id):
        page = []
        tags = []
        topic= ""
        try:
            connection = self.connect()
            query = "SELECT title,text,topic_id,id FROM pages WHERE id={}".format(str(page_id))

            with connection.cursor() as cursor:
                cursor.execute(query)
            for c in cursor:
                topic_id = c[2]
                page.append(c[0])#title
                page.append(c[1])#content
                page.append(c[3])#id


            topic,tags=self.getPageTopicTags(page_id,topic_id)

            return page, topic, tags
        except Exception as e:
            print(e)
            return page, topic, tags
        finally:
            connection.close()



    def getVideosForPage(self,page_id):

        videos = []

        try:
            connection = self.connect()
            video_ids=[]
            query = "SELECT video_id FROM pages_videos WHERE page_id={};".format(page_id)
            with connection.cursor() as cursor:
                cursor.execute(query)
            for c in cursor:
                video_ids.append(c[0])

            for v in video_ids:
                query = "SELECT link FROM videos WHERE id={};".format(v)
                with connection.cursor() as cursor:
                    cursor.execute(query)
                for c in cursor:
                    videos.append(c[0])
            return videos


        except Exception as e:
            print(e)
            return videos
        finally:
            connection.close()

        return topics

    def getTopics(self):
        topics = []

        try:
            connection = self.connect()
            query = "SELECT id,topic FROM topic;"
            with connection.cursor() as cursor:
                cursor.execute(query)
            for topic in cursor:
                article = [topic[0], topic[1]]
                topics.append(article)
                print(topic[0])
            # pages.reverse()
            return topics
        except Exception as e:
            print(e)
            return topics
        finally:
            connection.close()

        return topics

    def getTags(self):
        tags = []

        try:
            connection = self.connect()
            query = "SELECT id,tag FROM tags;"
            with connection.cursor() as cursor:
                cursor.execute(query)
            for tag in cursor:
                article = [tag[0], tag[1]]
                tags.append(article)
                print(tag[0])
            # pages.reverse()
            return tags
        except Exception as e:
            print(e)
            return tags
        finally:
            connection.close()

        return tags

    def getallpoints(self):
        connection = self.connect()
        named_projects = []
        try:
            query = "SELECT latitude,longitude,startdate,enddate,category,description FROM project;"
            with connection.cursor() as cursor:
                cursor.execute(query)
            for project in cursor:
                named_project = {
                    'latitude': project[0],
                    'longitude': project[1],
                    'startdate': project[2],#datetime.strftime(project[2], '%Y-%m-%d'),
                    'enddate': project[3],#datetime.strftime(project[3], '%Y-%m-%d'),
                    'category': project[4],
                    'description': project[5]
                }
                named_projects.append(named_project)
            # print(named_project)
            return json.dumps(named_projects)
        except Exception as e:
            print(e)
            testp = {
                'latitude': 51.758793,
                'longitude': -1.253667,
                'startdate': "200-01-01",
                'enddate': "200-01-01",
                'category': "research",
                'description': "test desc"
            }
            named_projects.append(testp)
            return json.dumps(named_projects)
        finally:
            connection.close()

    def get_all_inputs(self):
        connection = self.connect()
        named_projects = []
        try:
            query = "SELECT description FROM project;"
            with connection.cursor() as cursor:
                cursor.execute(query)
            for project in cursor:
                named_project = project[0]
                named_projects.append(named_project)
                print(named_project)
            return named_projects
        except Exception as e:
            print(e)
        finally:
            connection.close()

    def add_project(self, latitude, longitude, startdate, enddate, category, description):
        connection = self.connect()
        try:
            query = "INSERT INTO project (latitude,longitude,startdate,enddate,category,description) VALUES (%s,%s,%s,%s,%s,%s);"
            with connection.cursor() as cursor:
                cursor.execute(query, (latitude, longitude, startdate, enddate, category, description))
                connection.commit()
        except Exception as e:
            print(e)
        finally:
            connection.close()

    def uploadxls(self, filename):
        connection = self.connect()
        try:
            data = genfromtxt(filename, delimiter=',', skip_header=1,
                              converters={0: lambda s: str(s), 1: lambda s: str(s), 2: lambda s: str(s),
                                          3: lambda s: str(s), 4: lambda s: str(s), 5: lambda s: str(s)})
            data = data.tolist()
            for i in data:
                latitude = i[0]
                longitude = i[1]
                startdate = i[2]#datetime.strptime(i[2], '%Y-%m-%d').date()
                enddate = i[3]#datetime.strptime(i[3], '%Y-%m-%d').date()
                category = i[4]
                description = i[5]

                query = "INSERT INTO project (latitude,longitude,startdate,enddate,category,description) VALUES (%s,%s,%s,%s,%s,%s);"
                with connection.cursor() as cursor:
                    cursor.execute(query, (latitude, longitude, startdate, enddate, category, description))
                    connection.commit()
        except Exception as e:
            print(e)
        finally:
            connection.close()

    def uploadcsv(self, filename):
        connection = self.connect()
        try:
            data = genfromtxt(filename, delimiter=',', skip_header=1,
                              converters={0: lambda s: str(s), 1: lambda s: str(s), 2: lambda s: str(s),
                                          3: lambda s: str(s), 4: lambda s: str(s), 5: lambda s: str(s),
                                          6: lambda s: str(s), 7: lambda s: str(s)})

            print(data)
            data = data.tolist()
            print(data)
            for i in data:
                print(i)
                latitude = i[1]
                longitude = i[2]
                startdate=datetime.utcnow()
                enddate=datetime.utcnow()
                updated_at=datetime.utcnow()
                try:
                    startdate = datetime.strptime(i[3], '%Y-%m-%d').date()
                except Exception as e:
                    pass
                try:
                    enddate = datetime.strptime(i[4], '%Y-%m-%d').date()
                except Exception as e:
                    pass
                category = i[5]
                description = i[6]
                try:
                    enddate = datetime.strptime(i[7], '%Y-%m-%d').date()
                except Exception as e:
                    pass

                query = "INSERT INTO project (latitude,longitude,startdate,enddate,category,description,updated_at) VALUES (%s,%s,%s,%s,%s,%s,%s);"
                with connection.cursor() as cursor:
                    cursor.execute(query, (latitude, longitude, startdate, enddate, category, description,updated_at))
                    connection.commit()
        except Exception as e:
            print(e)
        finally:
            connection.close()

    def get_all_projects(self):
        connection = self.connect()
        named_projects = []
        try:
            query = "SELECT latitude,longitude,startdate,enddate,category,description FROM project;"
            with connection.cursor() as cursor:
                cursor.execute(query)
            for project in cursor:
                named_project = {
                    'latitude': project[0],
                    'longitude': project[1],
                    'startdate': project[2],#datetime.strftime(project[2], '%Y-%m-%d'),
                    'enddate': project[3],#datetime.strftime(project[3], '%Y-%m-%d'),
                    'category': project[4],
                    'description': project[5]
                }
                named_projects.append(named_project)
            # print(named_project)
            return named_projects
        except Exception as e:
            print(e)
            testp = {
                'latitude': 51.758793,
                'longitude': -1.253667,
                'startdate': "200-01-01",
                'enddate': "200-01-01",
                'category': "research",
                'description': "test desc"
            }
            named_projects.append(testp)
            return named_projects
        finally:
            connection.close()

    def get_columns(self, columns=['*']):
        connection = self.connect()
        projects = []
        try:
            query = "SELECT "+columns+" FROM project;"
            with connection.cursor() as cursor:
                cursor.execute(query)
            for project in cursor:
                thisp=[]
                for p in project:
                    print(p)
                    print(thisp)
                    thisp.append(p)
                projects.append(thisp)
            return projects
        except Exception as e:
            print(e)
            return projects
        finally:
            connection.close()

    def clear_all(self):
        connection = self.connect()
        try:
            query = "DELETE FROM project;"
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
        finally:
            connection.close()
