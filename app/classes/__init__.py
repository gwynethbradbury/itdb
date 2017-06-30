<<<<<<< HEAD
from flask_sqlalchemy import SQLAlchemy
from .. import app
database = SQLAlchemy(app)
import map as db_map
import it_lending_log as db_it_lending_log
import online_learning as db_online_learning
classesdict={
    'cls_map_project': db_map.Project,
    'cls_map_testtable': db_map.Testtable,
    'cls_map_emptytable': db_map.Emptytable,
    'cls_it_lending_log_items': db_it_lending_log.Items,
    'cls_it_lending_log_log': db_it_lending_log.Log,
    'cls_online_learning_videos': db_online_learning.Videos,
    'cls_online_learning_tags': db_online_learning.Tags,
    'cls_online_learning_pages_tags': db_online_learning.PagesTags,
    'cls_online_learning_topic': db_online_learning.Topic,
    'cls_online_learning_pages_videos': db_online_learning.PagesVideos,
    'cls_online_learning_pages': db_online_learning.Pages,
    }
=======
>>>>>>> 2d614dccacf231122a58729add0d11b86d8910ee
