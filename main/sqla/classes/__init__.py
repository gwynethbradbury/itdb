from flask_sqlalchemy import SQLAlchemy
from main.sqla.app import db as db
import map as db_map
import online_learning as db_online_learning
import it_lending_log as db_it_lending_log
classesdict={
    'cls_map_derp4': db_map.Derp4,
    'cls_map_project': db_map.Project,
    'cls_map_pro': db_map.Pro,
    'cls_map_derp2': db_map.Derp2,
    'cls_map_derp': db_map.Derp,
    'cls_online_learning_videos': db_online_learning.Videos,
    'cls_online_learning_tags': db_online_learning.Tags,
    'cls_online_learning_pages_tags': db_online_learning.PagesTags,
    'cls_online_learning_topic': db_online_learning.Topic,
    'cls_online_learning_pages_videos': db_online_learning.PagesVideos,
    'cls_online_learning_pages': db_online_learning.Pages,
    'cls_it_lending_log_items': db_it_lending_log.Items,
    'cls_it_lending_log_log': db_it_lending_log.Log,
    }
