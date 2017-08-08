from flask_sqlalchemy import SQLAlchemy
from main.sqla.app import db as db
import inspect
import importlib

db_list=['map','it_lending_log','online_learning']

classesdict={}
my_db = {}

for db_item in db_list:
  my_db[db_item]=importlib.import_module('.classes_master', __name__)
  my_db[db_item].init(db_item)
  # this doesn't work as we need to map to the class, not merely the name of the class!
  for i in my_db[db_item].class_list:
     classes_arr=i.split('_')
     cn=""
     for cl in classes_arr:
        cn=cn+cl.capitalize()
#     classesdict["cls_"+db_item+"_"+i] = 'my_db["'+db_item+'"].'+cn


classesdict={
    'cls_map_project': my_db['map'].Project,
    'cls_map_testtable': my_db['map'].Testtable,
    'cls_map_emptytable': my_db['map'].Emptytable,
    'cls_online_learning_videos': my_db['online_learning'].Videos,
    'cls_online_learning_tags': my_db['online_learning'].Tags,
    'cls_online_learning_pages_tags': my_db['online_learning'].PagesTags,
    'cls_online_learning_topic': my_db['online_learning'].Topic,
    'cls_online_learning_pages_videos': my_db['online_learning'].PagesVideos,
    'cls_online_learning_pages': my_db['online_learning'].Pages,
    'cls_it_lending_log_items': my_db['it_lending_log'].Items,
    'cls_it_lending_log_log': my_db['it_lending_log'].Log,
    }
