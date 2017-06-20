import json


class MockDBHelper:
    def __init__(self, dbname):
        self.mydatabase = dbname

    def connect(self, database=""):
        pass

    def getallpoints(self):
        connection = self.connect()
        named_projects = []
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

    def get_all_inputs(self):
        return [{'latitude': 51.758793, 'longitude': -1.253667, 'startdate': "200-01-01", 'enddate': "200-01-01",
                 'category': "research", 'description': "test desc"}]

    def add_input(self, data):
        pass

    def clear_all(self):
        pass

    def add_project(self, latitude, longitude, startdate, enddate, category, description):
        pass

    def get_all_projects(self):
        return [{'latitude': 51.758793, 'longitude': -1.253667, 'startdate': "200-01-01", 'enddate': "200-01-01",
                 'category': "research", 'description': "test desc"}]
