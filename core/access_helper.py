import pymysql
import dbconfig
from time import time
from datetime import datetime
from numpy import genfromtxt

#this needs to be updated dynamically. superusers=1

# usergroup_ID = 0
# if dbconfig.test:
#     usergroup_ID = 1

import iaasldap
from . import dict2

class AccessHelper:
    def connect(self, database="iaas"):
        return pymysql.connect(host='localhost',
                               user=dbconfig.db_user,
                               passwd=dbconfig.db_password,
                               db=database)

    def get_group_id(self,group_name):
        # todo:remove this conditional once tested
        # (assumes the user is a super user if no groupnames are found)
        if group_name=="":# and dbconfig.test:
            return 0

        connection = self.connect()
        group_id=0
        try:
            print("about to query...")
            usersgroups = iaasldap.get_groups(iaasldap.uid_trim())
            print("user {} is in groups {}".format(iaasldap.uid_trim(),
                                                   usersgroups))
            for g in usersgroups:

                query = "SELECT id " \
                        "FROM groups " \
                        "WHERE ldap_name='{}';"\
                    .format(group_name)

                with connection.cursor() as cursor:
                    cursor.execute(query)

                for inst in cursor:
                    instance = inst[0]
                    group_id = instance
            return group_id
        except Exception as e:
            print(e)
            return group_id
        finally:
            connection.close()

    def get_projects(self, svc_type):
        instances = []
        connection = self.connect()
        try:
            print("about to query...")
            usersgroups = iaasldap.get_groups(iaasldap.uid_trim())
            print("user {} is in groups {}".format(iaasldap.uid_trim(),
                                                   usersgroups))
            for g in usersgroups:
                g_id = self.get_group_id(g)
                query = "SELECT instance_identifier,project_display_name " \
                        "FROM svc_instances " \
                        "WHERE svc_type_id='{}' " \
                        "AND group_id='{}';"\
                    .format(str(svc_type),str(g_id))

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

    def get_projects_for_group(self, group):
        instances = []
        connection = self.connect()
        try:
            print("about to query...")
            usersgroups = iaasldap.get_groups(iaasldap.uid_trim())
            print("user {} is in groups {}".format(iaasldap.uid_trim(),
                                                   usersgroups))
            g_id = self.get_group_id(group)
            query = "SELECT instance_identifier,project_display_name,svc_type_id " \
                    "FROM svc_instances " \
                    "WHERE group_id='{}';"\
                .format(str(g_id))

            with connection.cursor() as cursor:
                cursor.execute(query)
            for inst in cursor:
                instance = [inst[0], inst[1], dict2[inst[2]]]
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
                print(ev[0])
            articles.reverse()
            return articles
        except Exception as e:
            print(e)
            return articles
        finally:
            connection.close()

    def get_mailing_list(self):
        subscribers = []
        try:
            connection = self.connect()
            print("about to query...")
            query = "SELECT email FROM subscribers;"
            with connection.cursor() as cursor:
                cursor.execute(query)
            for ev in cursor:
                subscriber = ev[0]
                subscribers.append(subscriber)
                print(ev[0])
            return subscribers
        except Exception as e:
            print(e)
            return subscribers
        finally:
            connection.close()

    def add_subscriber(self,name,email):
        try:
            connection=self.connect()
            print("adding {} ({}) to subscriber list".format(name,email))
            query = "INSERT INTO subscribers (name, email) VALUES ('{}', '{}');".format(name,email)
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
        except Exception as e:
            print(e)
        finally:
            connection.close()



