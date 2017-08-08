import pymysql
import dbconfig
connection = pymysql.connect(host=dbconfig.db_hostname,
				user=dbconfig.db_user,
				passwd=dbconfig.db_password)

try:
	with connection.cursor() as cursor:
		sql="CREATE DATABASE IF NOT EXISTS map"
		cursor.execute(sql)
		sql="""CREATE TABLE IF NOT EXISTS map.projects(
			id int NOT NULL AUTO_INCREMENT,
			latitude FLOAT(10,6),
			longitude FLOAT(10,6),
			startdate DATETIME,
			enddate DATETIME,
			category VARCHAR(50),
			description VARCHAR(1000),
			updated_at TIMESTAMP,
			PRIMARY KEY (id)
			)"""
		cursor.execute(sql);
	connection.commit()
finally:
	connection.close()

