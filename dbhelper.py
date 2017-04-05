import pymysql
import dbconfig
import datetime


class DBHelper:

	def connect(self,database="map"):
		return pymysql.connect(host='localhost',
				user=dbconfig.db_user,
				passwd=dbconfig.db_password,
				db=database)

	def get_all_inputs(self):
		connection=self.connect()
		try:
			query="SELECT description FROM projects;"
			with connection.cursor() as cursor:
				cursor.execute(query)
			return cursor.fetchall()
		finally:
			connection.close()

	def add_project(self, latitude,longitude,startdate,enddate,category,description):
		connection=self.connect()
		try:
			print("doop")
			query="INSERT INTO projects (latitude,longitude,startdate,enddate,category,description) VALUES (%s,%s,%s,%s,%s,%s);"
			with connection.cursor() as cursor:
				cursor.execute(query,(latitude,longitude,startdate,enddate,category,description))
				connection.commit()
				print("derp")
			print("deep")
		except Exception as e:
			print(e)
		finally:
			connection.close()

	def uploadxls(self, filename):
		connection=self.connect()
		try:#not working yet
			#query="LOAD DATA INFILE (%s) INTO TABLE projects;"
			#print(filename)
			#with connection.cursor() as cursor:
			#	cursor.execute(query,filename)
			#	connection.commit()
			print("uploadxls function not written")
		except Exception as e:
			print(e)
		finally:
			connection.close()

	def get_all_projects(self):
		connection=self.connect()
		try:
			query="SELECT latitude,longitude,startdate,enddate,category,description FROM projects;"
			with connection.cursor() as cursor:
				cursor.execute(query)
			named_projects=[]
			for project in cursor:
				named_project={
					'latitude':project[0],
					'longitude':project[1],
					'startdate':datetime.datetime.strftime(project[2],'%Y-%m-%d'),
					'enddate':datetime.datetime.strftime(project[3],'%Y-%m-%d'),
					'category':project[4],
					'description':project[5]
				}
				named_projects.append(named_project)
			return named_projects
		except Exception as e:
			print(e)
			return [{'latitude':51.758793,'longitude':-1.253667,'startdate':"200-01-01",'enddate':"200-01-01",'category':"research",'description':"test desc"}]
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
