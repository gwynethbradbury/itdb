import pymysql
import dbconfig
from time import time
from datetime import datetime
from numpy import genfromtxt





class MockAccessHelper:


	def get_projects(self,p):
		instances=[]
		instances= [['testlink','test']]
		return instances
	def get_events(self):
		events=[]
		events=[['test0','test1','test2','test3','monthname','m num','test5','test6']]
		return events
				
