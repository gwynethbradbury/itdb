<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 7af8c73cd5024fbaea1ac99e3bd3ed7445e0ed6b
from flask_sqlalchemy import SQLAlchemy
from .. import app
database = SQLAlchemy(app)
import map as db_map
<<<<<<< HEAD
import it_lending_log as db_it_lending_log
import online_learning as db_online_learning
classesdict={
    'cls_map_project': db_map.Project,
    'cls_map_testtable': db_map.Testtable,
    'cls_map_emptytable': db_map.Emptytable,
    'cls_it_lending_log_items': db_it_lending_log.Items,
    'cls_it_lending_log_log': db_it_lending_log.Log,
=======
import project2 as db_project2
import project3 as db_project3
import online_learning as db_online_learning
import it_lending_log as db_it_lending_log
import iaas as db_iaas
classesdict={
    'cls_map_derp4': db_map.Derp4,
    'cls_map_project': db_map.Project,
    'cls_map_pro': db_map.Pro,
    'cls_map_derp2': db_map.Derp2,
    'cls_map_derp': db_map.Derp,
    'cls_project3_newtable': db_project3.Newtable,
    'cls_project3_new_table': db_project3.NewTable,
>>>>>>> 7af8c73cd5024fbaea1ac99e3bd3ed7445e0ed6b
    'cls_online_learning_videos': db_online_learning.Videos,
    'cls_online_learning_tags': db_online_learning.Tags,
    'cls_online_learning_pages_tags': db_online_learning.PagesTags,
    'cls_online_learning_topic': db_online_learning.Topic,
    'cls_online_learning_pages_videos': db_online_learning.PagesVideos,
    'cls_online_learning_pages': db_online_learning.Pages,
<<<<<<< HEAD
    }
=======
>>>>>>> 2d614dccacf231122a58729add0d11b86d8910ee
=======
    'cls_it_lending_log_items': db_it_lending_log.Items,
    'cls_it_lending_log_log': db_it_lending_log.Log,
    'cls_iaas_comment': db_iaas.Comment,
    'cls_iaas_iaas_events': db_iaas.IaasEvents,
    'cls_iaas_permitted_svc': db_iaas.PermittedSvc,
    'cls_iaas_subscribers': db_iaas.Subscribers,
    'cls_iaas_blog': db_iaas.Blog,
    'cls_iaas_svc_instances': db_iaas.SvcInstances,
    'cls_iaas_roles': db_iaas.Roles,
    'cls_iaas_groups': db_iaas.Groups,
    'cls_iaas_services': db_iaas.Services,
    'cls_iaas_News': db_iaas.News,
    'cls_iaas_users': db_iaas.Users,
    }
>>>>>>> 7af8c73cd5024fbaea1ac99e3bd3ed7445e0ed6b
