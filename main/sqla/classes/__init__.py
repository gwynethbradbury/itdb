from flask_sqlalchemy import SQLAlchemy
from main.sqla.app import db as db
import inspect

#classesdict={}

import classes_master as db_map
db_map.init('map')
# this doesn't work as db_map.Project is not a string - needs to be extracted from globals :(
#for i in db_map.class_list:
#   classes_arr=i.split('_')
#   cn=""
#   for cl in classes_arr:
#      cn=cn+cl.capitalize()
#   classesdict["cls_"+map+"_"+i] = 'db_map.'+cn

import classes_master as db_it_lending_log
db_it_lending_log.init('it_lending_log')
import classes_master as db_online_learning
db_online_learning.init('online_learning')



classesdict={
    'cls_map_project': db_map.Project,
    'cls_map_testtable': db_map.Testtable,
    'cls_map_emptytable': db_map.Emptytable,
    'cls_online_learning_videos': db_online_learning.Videos,
    'cls_online_learning_tags': db_online_learning.Tags,
    'cls_online_learning_pages_tags': db_online_learning.PagesTags,
    'cls_online_learning_topic': db_online_learning.Topic,
    'cls_online_learning_pages_videos': db_online_learning.PagesVideos,
    'cls_online_learning_pages': db_online_learning.Pages,
    'cls_it_lending_log_items': db_it_lending_log.Items,
    'cls_it_lending_log_log': db_it_lending_log.Log,
    }
