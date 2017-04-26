The process for creating a new project should be roughly as follows:


1. Clone the basic project (currently 'map') files in projects/[basic project] and templates/projects/[basic project]

2. Mysql: create the empty database and grant permissions to the iaas user (this username might change in future)

3. add the new project database to the list of binds in the dbconfig.py file

4. Adjust the model file in projects/[new project name]/models.py
- add the classes corresponding to the new tables 
- ensure classes contain the right __key_binding__ flag for the newly created database name
- avoid capitalising the first letter or a class name as this seems to lead to discrepancies between different sql versions and breaks the pages

5. Start a python console:

import dbconfig, config
from app import db
from projects.[new project name].models import *
db.create_all(bind = ‘[db bind name]’)


6. To add the admin pages for this project, add the following lines to the project's __init__.py file
- adjust for each corresponding class/table (class and table names should be the same)
register_crud(map, '/[new project name]/map/admin/[table name]', '[class name]', [class name])