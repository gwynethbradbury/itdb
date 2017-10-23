from datetime import datetime

import pymysql

import dbconfig
from ...auth.iaasldap import LDAPUser as iaasldap
from . import dict1, dict2
from ...iaas.iaas import SvcInstance,DatabaseInstance,NextcloudInstance,WebApp,Group

iaasldap = iaasldap()


# this needs to be updated dynamically. superusers=1
# usergroup_ID = 0
# if dbconfig.test:
#     usergroup_ID = 1

class AccessHelper:
    def connect(self, database=dbconfig.db_name):
        return pymysql.connect(host=dbconfig.db_hostname,
                               user=dbconfig.db_user,
                               passwd=dbconfig.db_password,
                               db=database)

    def get_group_id(self, group_name):
        # todo:remove this conditional once tested
        # (assumes the user is a super user if no groupnames are found)
        if group_name == "":  # and dbconfig.test:
            return 0



        inst = Group.query.filter_by(ldap_name=group_name).first
        group_id = inst.id

        return group_id

    def get_projects(self, svc_type):
        instances = []
        usersgroups = iaasldap.get_groups()

        for g in usersgroups:
            if svc_type=='dbas':
                p= DatabaseInstance.query.filter_by(group_id=g).all()
                instance = [p.svc_instance.instance_identifier, p.svc_instance.project_display_name, dict2[p.svc_instance.svc_type_id]]
                instances.append(instance)
            elif svc_type=='nc':
                p= NextcloudInstance.query.filter_by(group_id=g).all()
                instance = [p.svc_instance.instance_identifier, p.svc_instance.project_display_name, dict2[p.svc_instance.svc_type_id]]
                instances.append(instance)
            elif svc_type=='waas':
                p= WebApp.query.filter_by(group_id=g).all()
                instance = [p.svc_inst.instance_identifier, p.svc_inst.project_display_name, dict2[p.svc_inst.svc_type_id]]
                instances.append(instance)

        return instances


    def get_projects_for_group(self, group):
        instances = []
        connection = self.connect()
        try:
            g_id = self.get_group_id(group)
            if not group == 'superusers':# or svc_type>=0:
                projects = SvcInstance.query.filter_by(group_id=g_id).all()
            else:
                projects = SvcInstance.query.all()
            for p in projects:
                instance = [p.instance_identifier, p.project_display_name, dict2[p.svc_type_id]]
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
        futureevents = []
        nowevents = []
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
                if datetime.now().date() < ev[4]:
                    futureevents.append(event)
                elif datetime.now().date() > ev[4]:
                    pastevents.append(event)
                elif datetime.now().date() == ev[4]:
                    nowevents.append(event)

            return [pastevents, nowevents, futureevents]
        except Exception as e:
            print(e)
            return [pastevents, nowevents, futureevents]
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

    def add_subscriber(self, name, email):
        try:
            connection = self.connect()
            print("adding {} ({}) to subscriber list".format(name, email))
            query = "INSERT INTO subscribers (name, email) VALUES ('{}', '{}');".format(name, email)
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
        except Exception as e:
            print(e)
        finally:
            connection.close()

    def getDatabaseConnectionString(self, db_name):
        # todo:remove this conditional once tested
        # (assumes the user is a super user if no groupnames are found)

        project_owner="project owner"
        project_maintainer="project maintainer"
        ip_address="not set"
        svc_inst=""
        port=-1
        username="not set"
        password_if_secure="not ser or insecure"
        description="Optional"
        engine_type=""
        engine_string=""
        if db_name == "":  # and dbconfig.test:
            return project_owner, project_maintainer, ip_address, svc_inst, port, username, password_if_secure,description, engine_type, engine_string

        connection = self.connect()
        try:
            query = "SELECT id,svc_type_id " \
                    "FROM svc_instances " \
                    "WHERE instance_identifier='{}';" \
                .format(db_name)

            with connection.cursor() as cursor:
                cursor.execute(query)

            for inst in cursor:
                id = inst[0]
                svc_type_id=inst[1]

            if not svc_type_id==1:
                return project_owner, project_maintainer, ip_address, svc_inst, port, username, password_if_secure, description, engine_type, engine_string

            query = "SELECT project_owner, project_maintainer, ip_address, svc_inst, port, " \
                    "username, password_if_secure, description, engine_type " \
                    "FROM database_instances " \
                    "WHERE svc_inst='{}';" \
                .format(id)

            with connection.cursor() as cursor:
                cursor.execute(query)

            for inst in cursor:
                project_owner = inst[0]
                project_maintainer = inst[1]
                ip_address=inst[2]
                svc_inst=inst[3]
                port=inst[4]
                username=inst[5]
                password_if_secure=inst[6]
                description=inst[7]
                engine_type_ind=inst[8]

            query = "SELECT connection_string, name " \
                    "FROM database_engine " \
                    "WHERE id='{}';" \
                .format(engine_type_ind)

            with connection.cursor() as cursor:
                cursor.execute(query)

            for inst in cursor:
                engine_string = inst[0]
                engine_type = inst[1]

            return project_owner, project_maintainer, ip_address, svc_inst, port, username, password_if_secure,description,engine_type,engine_string

        except Exception as e:
            print(e)
        finally:
            connection.close()

        return project_owner, project_maintainer, ip_address, svc_inst, port, username, password_if_secure,description,engine_type,engine_string

