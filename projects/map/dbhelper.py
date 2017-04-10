import pymysql
import dbconfig
from time import time
from datetime import datetime
from numpy import genfromtxt





class DBHelper:
	def connect(self,database="map"):
		return pymysql.connect(host='localhost',
				user=dbconfig.db_user,
				passwd=dbconfig.db_password,
				db=database)

	def get_all_inputs(self):
		connection=self.connect()
		named_projects=[]
		try:
			query="SELECT description FROM projects;"
			with connection.cursor() as cursor:
				cursor.execute(query)
			for project in cursor:
				named_project= project[0]
				named_projects.append(named_project)
				print(named_project)
			return named_projects
		except Exception as e:
			print(e)
		finally:
			connection.close()

	def add_project(self, latitude,longitude,startdate,enddate,category,description):
		connection=self.connect()
		try:
			query="INSERT INTO projects (latitude,longitude,startdate,enddate,category,description) VALUES (%s,%s,%s,%s,%s,%s);"
			with connection.cursor() as cursor:
				cursor.execute(query,(latitude,longitude,startdate,enddate,category,description))
				connection.commit()
		except Exception as e:
			print(e)
		finally:
			connection.close()

	def uploadxls(self, filename):
		connection=self.connect()
		try:
			data=genfromtxt(filename,delimiter=',',skip_header=1,converters={0: lambda s: str(s),1: lambda s: str(s),2: lambda s: str(s),3: lambda s: str(s),4: lambda s: str(s),5: lambda s: str(s)})
			data=data.tolist()
			for i in data:

				latitude=i[0]
				longitude=i[1]
				startdate=datetime.strptime(i[2],'%Y-%m-%d').date()
				enddate=datetime.strptime(i[3],'%Y-%m-%d').date()
				category=i[4]
				description=i[5]

				query="INSERT INTO projects (latitude,longitude,startdate,enddate,category,description) VALUES (%s,%s,%s,%s,%s,%s);"
				with connection.cursor() as cursor:
					cursor.execute(query,(latitude,longitude,startdate,enddate,category,description))
					connection.commit()
		except Exception as e:
			print(e)
		finally:
			connection.close()

	def get_all_projects(self):
		connection=self.connect()
		named_projects=[]
		try:
			query="SELECT latitude,longitude,startdate,enddate,category,description FROM projects;"
			with connection.cursor() as cursor:
				cursor.execute(query)
			for project in cursor:
				named_project={
					'latitude':project[0],
					'longitude':project[1],
					'startdate':datetime.strftime(project[2],'%Y-%m-%d'),
					'enddate':datetime.strftime(project[3],'%Y-%m-%d'),
					'category':project[4],
					'description':project[5]
				}
				named_projects.append(named_project)
				#print(named_project)
			return named_projects
		except Exception as e:
			print(e)
			testp ={
					'latitude':51.758793,
					'longitude':-1.253667,
					'startdate':"200-01-01",
					'enddate':"200-01-01",
					'category':"research",
					'description':"test desc"
				}
			named_projects.append(testp)
			return named_projects
		finally:
			connection.close()

	def clear_all(self):
		connection=self.connect()
		try:
			query="DELETE FROM projects;"
			with connection.cursor() as cursor:
				cursor.execute(query)
				connection.commit()
		finally:
			connection.close()
