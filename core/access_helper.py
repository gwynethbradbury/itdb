import pymysql
import dbconfig
from time import time
from datetime import datetime
from numpy import genfromtxt

#this needs to be updated dynamically. superusers=1

usergroup_ID = 0
# if dbconfig.test:
#     usergroup_ID = 1



class AccessHelper:
    def connect(self, database="iaas"):
        return pymysql.connect(host='localhost',
                               user=dbconfig.db_user,
                               passwd=dbconfig.db_password,
                               db=database)

    def get_projects(self, svc_type):
        instances = []
        connection = self.connect()
        try:
            print("about to query...")
            query = "SELECT instance_identifier,project_display_name " \
                    "FROM svc_instances " \
                    "WHERE svc_type_id=" + str(svc_type) + \
                    " AND group_id=" + str(usergroup_ID) + ";"
            with connection.cursor() as cursor:
                cursor.execute(query)
            for inst in cursor:
                instance = [inst[0], inst[1]]
                instances.append(instance)
            return instances
        except Exception as e:
            print(e)
            instance = ['brokenlink', 'broken']
            instances.append(instance)
            for inst in instances:
                print(inst)
            return instances
        finally:
            connection.close()

    def get_events(self):
        pastevents = []
        futureevents=[]
        nowevents=[]
        try:
            connection = self.connect()
            print("about to query...")
            query = "SELECT title,subtitle,description,room,eventdate,starttime,endtime " \
                    "FROM iaas_events;"
            with connection.cursor() as cursor:
                cursor.execute(query)
            for ev in cursor:
                event = [ev[0], ev[1], ev[2], ev[3], datetime.strftime(ev[4], '%B'), datetime.strftime(ev[4], '%d'),
                         ev[5], ev[6]]
                print(datetime.now())
                if datetime.now().date()<ev[4]:
                    futureevents.append(event)
                elif datetime.now().date()>ev[4]:
                    pastevents.append(event)
                elif datetime.now().date()==ev[4]:
                    nowevents.append(event)

            return [pastevents,nowevents,futureevents]
        except Exception as e:
            print(e)
            return [pastevents,nowevents,futureevents]
        finally:
            connection.close()

    def get_news(self):
        articles = []
        try:
            connection = self.connect()
            print("about to query...")
            query = "SELECT title,body,updated_on FROM news;"
            with connection.cursor() as cursor:
                cursor.execute(query)
            for ev in cursor:
                article = [ev[0], ev[1], datetime.strftime(ev[2], '%B'), datetime.strftime(ev[2], '%d')]
                articles.append(article)
            return articles
        except Exception as e:
            print(e)
            return articles
        finally:
            connection.close()
