from flask import render_template, redirect, url_for, request,send_file
import json

# todo: remove dependence on DB, this functionality should be all in the DBA
import dbconfig
if dbconfig.test:
    from projects.map.mockdbhelper import MockDBHelper as DBHelper
else:
    from projects.map.dbhelper import DBHelper




def assignroutes(application,nm=""):
    approute = "/projects/"+nm+"/"
    DB = DBHelper(nm)

    @application.route(approute+"webapp/showpoints")
    def showpoints():
        projects = []
        try:
            data = DB.getallpoints()
            print(data)
            projects = DB.get_all_projects()
            projects = json.dumps(projects)
        except Exception as e:
            print e
            data = []
        print(data)
        return render_template(approute+nm+".html",
                               projects=projects, data=data)

    @application.route(approute+"webapp/submitproject", methods=['GET', 'POST'])
    def submit():
        try:
            category = request.form.get("category")
            startdate = request.form.get("startdate")
            enddate = request.form.get("enddate")
            latitude = float(request.form.get("latitude"))
            longitude = float(request.form.get("longitude"))
            description = request.form.get("description")
            DB.add_project(latitude, longitude, startdate, enddate, category, description)
        except Exception as e:
            print e
        # home()
        return redirect(url_for(nm+"_app."+nm))

    @application.route(approute+"webapp")
    def applicationhome():
        projects = []
        try:
            data = DB.get_all_inputs()
            projects = DB.get_all_projects()
            projects = json.dumps(projects)
        except Exception as e:
            print e
            data = []
        print(data)
        return render_template(approute+nm+".html",
                               projects=projects, data=data)





