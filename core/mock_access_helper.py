import pymysql
import dbconfig
from time import time
from datetime import datetime
from numpy import genfromtxt


class MockAccessHelper:
    def get_group_id(selfself, group_name):
        return 0

    def get_projects(self, p):
        instances = []
        instances = [['testlink', 'test']]
        return instances

    def get_projects_for_group(selfself, group):
        instances = [['testaddress', 'testname', 'testservicetype']]
        return instances

    def get_events(self):
        events = []
        events = [['test0', 'test1', 'test2', 'test3', 'monthname', 'm num', 'test5', 'test6']]
        return events

    def get_news(self):
        pass

    def get_mailing_list(self):
        subscribers = [['testsubscriber']]
        return subscribers

    def add_subscriber(self, name, email):
        pass
