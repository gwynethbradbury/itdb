import pymysql
import dbconfig


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

	def add_input(self,data):
		connection=self.connect()
		try:
			#introduces a security flaw:
			query="INSERT INTO projects (description) VALUES ('{}');".format(data)			
			with connection.cursor() as cursor:
				cursor.execute(query)
				connection.commit()
		finally:
			conncetion.close()

	def clear_all(self):
		connection=self.connect()
		try:
			query="DELETE FROM projects;"	
			with connection.cursor() as cursor:
				cursor.execute(query)
				connection.commit()			
		finally:
			conncetion.close()
	
