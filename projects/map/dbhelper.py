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
                    'startdate': datetime.strftime(project[2], '%Y-%m-%d'),
                    'enddate': datetime.strftime(project[3], '%Y-%m-%d'),
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
                startdate = datetime.strptime(i[2], '%Y-%m-%d').date()
                enddate = datetime.strptime(i[3], '%Y-%m-%d').date()
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
                    'startdate': datetime.strftime(project[2], '%Y-%m-%d'),
                    'enddate': datetime.strftime(project[3], '%Y-%m-%d'),
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
