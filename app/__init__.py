# project/__init__.py

from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
import dbconfig


app = Flask('dbas_app')
app.config.update(
        DEBUG=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///../database.db',
    )

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@localhost/iaas'.format(dbconfig.db_user, dbconfig.db_password)

db = SQLAlchemy(app)


from admin import admin

app.register_blueprint(admin, url_prefix='/admin', template_folder='templates')


@app.route('/admin')
def home():
    # instances=[]
    #
    # connection=self.connect()
    # try:
    # 	print("about to query...")
    # 	query="SELECT instance_identifier,project_display_name FROM svc_instances WHERE svc_type_id="+str(svc_type)+" AND group_id=1;"
    # 	with connection.cursor() as cursor:
    # 		cursor.execute(query)
    # 	for inst in cursor:
    # 		instance=[inst[0],inst[1]]
    # 		instances.append(instance)
    # 	return instances
    # except Exception as e:
    # 	print(e)
    # 	instances= ['test']
    # 	for inst in instances:
    # 		print(inst)
    # 	return instances
    # finally:
    # 	connection.close()
    #
    #
    #instances = []
    #try:
    #    instances.append('map')
    #    instances.append('another app')
    #except Exception as e:
    #    print e
    #for inst in instances:
    #    print(inst)
    #    return render_template("index.html", instances=instances)
    return 'dbas admin home <br/> should return a list of dbas services with means to add or remove if the user is superuser'

