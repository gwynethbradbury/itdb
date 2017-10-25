from datetime import datetime

import pymysql

import dbconfig
from ...auth.iaasldap import LDAPUser as iaasldap
from . import dict1, dict2
from ...iaas.iaas import SvcInstance,DatabaseInstance,NextcloudInstance,WebApp,Group,News,Subscriber,IaasEvent,db

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



        inst = Group.query.filter_by(ldap_name=group_name).first()
        group_id = inst.id

        return group_id

    def get_projects(self, svc_type):
        instances = []
        usersgroups = iaasldap.get_groups()
        for group in usersgroups:
            g = (Group.query.filter_by(ldap_name=group).first()).id
            svcs = SvcInstance.query.filter_by(group_id=g)
            for s in svcs:
                if svc_type=='dbas':
                    for p in s.databases:
                        instance = [s.instance_identifier, "{} ({})".format(s.project_display_name,p.database_name)]
                        instances.append(instance)
                elif svc_type=='nc':
                    for p in s.nextclouds:
                        instance = ["/projects/"+s.instance_identifier, s.project_display_name +" (NextCloud)"]
                        instances.append(instance)
                elif svc_type=='waas':
                    for p in s.webapps:
                        instance = [s.instance_identifier, "{} ({})".format(s.project_display_name,p.name)]
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
                instance = [p.instance_identifier, p.project_display_name]
                instances.append(instance)


            return instances
        except Exception as e:
            print(e)
            instance = ['brokenlink', 'broken']
            instances.append(instance)
            # for inst in instances:
            #     print(inst)
            return instances
        finally:
            connection.close()

    def get_events(self):
        events = IaasEvent.query.order_by(IaasEvent.eventdate.asc()).all()
        pastevents = []
        futureevents = []
        nowevents = []
        for e in events:
            if e.eventdate<datetime.now().date():
                pastevents.append(e)
            elif e.eventdate>datetime.now().date():
                futureevents.append(e)
            else:
                nowevents.append(e)


        return [pastevents, nowevents, futureevents]



    def get_news(self):
        articles = News.query.order_by(News.created_on.asc()).all()
        return articles
        articles = []
        try:
            connection = self.connect()
            # print("about to query...")
            query = "SELECT title,body,updated_on FROM news;"
            with connection.cursor() as cursor:
                cursor.execute(query)
            for ev in cursor:
                article = [ev[0], ev[1], datetime.strftime(ev[2], '%B'), datetime.strftime(ev[2], '%d')]
                articles.append(article)
                # print(ev[0])
            articles.reverse()
            return articles
        except Exception as e:
            print(e)
            return articles
        finally:
            connection.close()

    def get_mailing_list(self):
        subscribers = Subscriber.query.all()
        s_list=[]
        for s in subscribers:
            s_list.append(s.email)
        return s_list

    def add_subscriber(self, name, email):
        try:
            s = Subscriber(name,email)
            db.session.add(s)
            db.session.commit()
            return True
        except Exception as e:
            return False


    # def getDatabaseConnectionString(self, db_name):
    #     # todo:remove this conditional once tested
    #     # (assumes the user is a super user if no groupnames are found)
    #
    #     project_owner="project owner"
    #     project_maintainer="project maintainer"
    #     ip_address="not set"
    #     svc_inst=""
    #     port=-1
    #     username="not set"
    #     password_if_secure="not ser or insecure"
    #     description="Optional"
    #     engine_type=""
    #     engine_string=""
    #     if db_name == "":  # and dbconfig.test:
    #         return project_owner, project_maintainer, ip_address, svc_inst, port, username, password_if_secure,description, engine_type, engine_string
    #
    #     connection = self.connect()
    #     try:
    #         query = "SELECT id,svc_type_id " \
    #                 "FROM svc_instances " \
    #                 "WHERE instance_identifier='{}';" \
    #             .format(db_name)
    #
    #         with connection.cursor() as cursor:
    #             cursor.execute(query)
    #
    #         for inst in cursor:
    #             id = inst[0]
    #             svc_type_id=inst[1]
    #
    #         if not svc_type_id==1:
    #             return project_owner, project_maintainer, ip_address, svc_inst, port, username, password_if_secure, description, engine_type, engine_string
    #
    #         query = "SELECT project_owner, project_maintainer, ip_address, svc_inst, port, " \
    #                 "username, password_if_secure, description, engine_type " \
    #                 "FROM database_instances " \
    #                 "WHERE svc_inst='{}';" \
    #             .format(id)
    #
    #         with connection.cursor() as cursor:
    #             cursor.execute(query)
    #
    #         for inst in cursor:
    #             project_owner = inst[0]
    #             project_maintainer = inst[1]
    #             ip_address=inst[2]
    #             svc_inst=inst[3]
    #             port=inst[4]
    #             username=inst[5]
    #             password_if_secure=inst[6]
    #             description=inst[7]
    #             engine_type_ind=inst[8]
    #
    #         query = "SELECT connection_string, name " \
    #                 "FROM database_engine " \
    #                 "WHERE id='{}';" \
    #             .format(engine_type_ind)
    #
    #         with connection.cursor() as cursor:
    #             cursor.execute(query)
    #
    #         for inst in cursor:
    #             engine_string = inst[0]
    #             engine_type = inst[1]
    #
    #         return project_owner, project_maintainer, ip_address, svc_inst, port, username, password_if_secure,description,engine_type,engine_string
    #
    #     except Exception as e:
    #         print(e)
    #     finally:
    #         connection.close()
    #
    #     return project_owner, project_maintainer, ip_address, svc_inst, port, username, password_if_secure,description,engine_type,engine_string

