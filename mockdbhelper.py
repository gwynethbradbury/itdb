class MockDBHelper:
	def connect(self,database="map"):
		pass
	def get_all_inputs(self):
		return []
	def add_input(self,data):
		pass
	def clear_all(self):
		pass
	def add_project(self, latitude,longitude,startdate,enddate,category,description):
		pass
	def get_all_projects(self):
		return [{'latitude':51.758793,'longitude':-1.253667,'startdate':"200-01-01",'enddate':"200-01-01",'category':"research",'description':"test desc"}]
