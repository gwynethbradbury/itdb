from app.dev import *
from app import app as application
# from app import dictionary_of_databases
from flask import render_template, redirect, url_for, request, send_file
import json, os
from wtforms.ext.sqlalchemy.orm import model_form
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from werkzeug.utils import secure_filename


templateroute = "/projects/"


def render_detail(tablename, DBA, **kwargs):
    t, c = DBA.getTableAndColumnNames()
    path = "%s%s/" % (DBA.adminroute, tablename)  # url_for('.%s' % tablename)
    return render_template(DBA.detail_template, path=path,
                           tablenames=t,
                           pname=DBA.mydatabasename,
                           username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                           **kwargs)

def render_list(tablename, fields, DBA, **kwargs):
    t, c = DBA.getTableAndColumnNames()
    path = "%s%s/" % (DBA.adminroute, tablename)  # url_for('.%s' % tablename)
    return render_template(DBA.list_template, path=path,
                           fields=fields,
                           tablenames=t,
                           tablename=tablename,
                           filters=DBA.filters,
                           pname=DBA.mydatabasename,
                           username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                           **kwargs)


'''
Determines whether a user is authorised to view this project
caveat: if this is an admin-only page, _admin is added to the group name
'''
def user_authorised(application_name,is_admin_only_page=False):
    if is_admin_only_page:
        application_name = application_name +"_admin"
    usersgroups = iaasldap.get_groups(iaasldap.uid_trim())
    if application_name in usersgroups:
        return True
    if "superusers" in usersgroups:
        return True
    return False
##########PATHS###########


import core.iaasldap as iaasldap
from flask import abort

# home
@application.route("/projects/<application_name>/")
def showhome(application_name):
    if not user_authorised(application_name=application_name,is_admin_only_page=False):
        return abort(401)
    DBA = dictionary_of_databases[application_name]
    tablenames, columnnames = DBA.getTableAndColumnNames()

    print("tablenames are:")
    print(tablenames)
    print("end")
    return render_template(templateroute + "project_home.html",
                           tablenames=tablenames,
                           pname=application_name,
                           username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname())

# region VIEWING DATA


# list the tables
@application.route("/projects/<application_name>/admin/")
def showtables(application_name):
    if not user_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)

    DBA = dictionary_of_databases[application_name]
    tablenames, columnnames = DBA.getTableAndColumnNames()

    print("tablenames are:")
    print(tablenames)
    print("end")
    return render_template(templateroute + "project_admin.html",
                           tablenames=tablenames,
                           pname=application_name,
                           username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname())


# show the list vew for a given table in the DB
@application.route("/projects/<application_name>/admin/<tablename>/")
def showTable(application_name,tablename):
    if not user_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)
    DBA = dictionary_of_databases[application_name]
    tns, cns = DBA.getTableAndColumnNames(tablename=tablename)
    try:
        model = DBA.classFromTableName(classname=str(tablename), fields=cns[0])

        sesh = sessionmaker(bind=DBA.DBE.E)
        sesh = sesh()
        # ObjForm = model_form(model, sesh, exclude=None)

        q = select(from_obj=model, columns=['*'])
        result = sesh.execute(q)

        KEYS = result.keys()
        obj = []
        for r in result:
            obj.append(r)

        return render_list(tablename=tablename, obj=obj, fields=KEYS, DBA=DBA)
    except Exception as e:
        print(e)

    adminroute = "/projects/" + application_name + "/admin/"
    return redirect(adminroute)


# Show the detail view for a given entry in a given table
@application.route("/projects/<application_name>/admin/<tablename>/<obj_id>")
def displayObject(application_name,tablename,obj_id):
    if not user_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)
    DBA = dictionary_of_databases[application_name]

    if obj_id:
        tns,cns = DBA.getTableAndColumnNames(tablename=tablename)
        model = DBA.classFromTableName(classname=str(tablename), fields=cns[0])
        sesh = sessionmaker(bind=DBA.DBE.E)
        sesh = sesh()

        # this creates the form fields base on the model
        # so we don't have to do them one by one
        ObjForm = model_form(model, sesh)

        obj = sesh.query(model).filter_by(id=obj_id).first()
        # populate the form with our blog data
        form = ObjForm(obj=obj)
        # action is the url that we will later use
        # to do post, the same url with obj_id in this case
        action = request.path
        return render_detail(tablename=tablename,form=form, action=action, DBA=DBA)

    tns, cns = DBA.getTableAndColumnNames(tablename=tablename)
    model = DBA.classFromTableName(classname=str(tablename), fields=cns[0])
    sesh = sessionmaker(bind=DBA.DBE.E)
    sesh = sesh()

    # this creates the form fields base on the model
    # so we don't have to do them one by one
    ObjForm = model_form(model, sesh)

    obj = sesh.query(model).filter_by(id=obj_id).first()
    # populate the form with our blog data
    form = ObjForm(obj=obj)
    # action is the url that we will later use
    # to do post, the same url with obj_id in this case
    action = request.path
    return render_detail(form=form, action=action, DBA=DBA)


# apply a filter to the list view for a table
#todo: test filters
@application.route("/projects/<application_name>/admin/<tablename>/filter/<filter_name>")
def filterObjects(application_name,tablename, filter_name):
    if not user_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)
    DBA = dictionary_of_databases[application_name]
    tns,cns = DBA.getTableAndColumnNames(tablename=tablename)
    model = DBA.classFromTableName(classname=str(tablename),fields=cns[0])

    func = DBA.filters.get(filter_name)
    obj = func(model)

    return render_list(tablename=tablename, obj=obj, fields=obj.fields, filter_name=filter_name, DBA=DBA)
    pass

# endregion

# region EDITING TABLES

# creating a new table
@application.route("/projects/<application_name>/admin/newtable")
def newtable(application_name):
    if not user_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)
    DBA = dictionary_of_databases[application_name]

    tablenames,columnnames=DBA.getTableAndColumnNames()

    return render_template(templateroute+"create_table.html",
                           tablenames=tablenames,
                           columnnames=columnnames,
                           pname=application_name,
                           username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname())

# adding a column to an existing table
# todo: unfinished
@application.route("/projects/<application_name>/admin/addcolumn")
def addcolumn(application_name):
    if not user_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)
    DBA = dictionary_of_databases[application_name]

    tablenames, columnnames = DBA.getTableAndColumnNames()

    DBA.addColumn("newtable", "test2","Time stamp")

    return render_template(templateroute+"create_table.html",
                           tablenames=tablenames,
                           columnnames=columnnames,
                           pname=application_name,
                           username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname())

    # delete a whole table

@application.route("/projects/<application_name>/admin/deletetable/<page>")
def deletetable(application_name,page):
    if not user_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)
    DBA = dictionary_of_databases[application_name]
    DBA.deleteTable(page)
    # DBA.DBE.refresh()
    return redirect("/projects/"+application_name+"/admin/")

# clear all entries from a table
@application.route("/projects/<application_name>/admin/cleartable/<page>")
def cleartable(application_name,page):
    if not user_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)
    DBA = dictionary_of_databases[application_name]

    DBA.clearTable(page)
    return redirect("/projects/"+application_name+"/admin/")

# endregion

# region EDITING AND CREATING AN ITEM

# Generate the form for creating a new item
@application.route("/projects/<application_name>/admin/<tablename>/new")
def newObjectForm(application_name,tablename):
    if not user_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)
    DBA = dictionary_of_databases[application_name]

    tns, cns = DBA.getTableAndColumnNames(tablename=tablename)
    model = DBA.classFromTableName(classname=str(tablename), fields=cns[0])
    sesh = sessionmaker(bind=DBA.DBE.E)
    sesh = sesh()

    path = "%s%s/" %("/projects/"+application_name+"/admin/",tablename)
    ObjForm = model_form(model, sesh, exclude=None)
    #  we just want an empty form
    form = ObjForm()
    action = "%s" %("createnew")
    return render_detail(tablename=tablename, form=form, action=action, DBA=DBA)

# create the item based on the class and form responses
@application.route("/projects/<application_name>/admin/<tablename>/createnew",
                   methods=['GET', 'POST'])
def createnew(application_name,tablename, obj_id=''):
    if not user_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)
    DBA = dictionary_of_databases[application_name]
    tns, cns = DBA.getTableAndColumnNames(tablename=tablename)
    model = DBA.classFromTableName(classname=str(tablename), fields=cns[0])
    sesh = sessionmaker(bind=DBA.DBE.E)
    sesh = sesh()
    # either load and object to update if obj_id is given
    # else initiate a new object, this will be helpfull
    # when we want to create a new object instead of just
    # editing existing one
    if obj_id:
        obj = sesh.query(model).filter_by(id=obj_id).first()
    else:
        obj = model()

    ObjForm = model_form(model, sesh)
    # populate the form with the request data
    form = ObjForm(request.form)
    # this actually populates the obj (the blog post)
    # from the form, that we have populated from the request post
    form.populate_obj(obj)

    # db.session.add(obj)
    sesh.add(obj)
    sesh.commit()

    path = "%s%s/" % ("/projects/"+application_name+"/admin/", tablename)  # url_for('.%s' % tablename)
    return redirect(path)

# delete an item
@application.route("/projects/<application_name>/admin/<tablename>/delete/<id>/")
def deleteObject(application_name,tablename, id):
    if not user_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)
    DBA = dictionary_of_databases[application_name]
    tns, cns = DBA.getTableAndColumnNames(tablename=tablename)
    model = DBA.classFromTableName(classname=str(tablename), fields=cns[0])

    sesh = sessionmaker(bind=DBA.DBE.E)
    sesh = sesh()
    # ObjForm = model_form(model, sesh, exclude=None)

    obj = sesh.query(model).filter_by(id=id).first()
    sesh.delete(obj)
    sesh.commit()

    q = select(from_obj=model, columns=['*'])
    result = sesh.execute(q)

    KEYS = result.keys()
    obj = []
    for r in result:
        obj.append(r)

    return render_list(tablename=tablename, obj=obj, fields=KEYS, DBA=DBA)

# endregion

# region UPLOADING AND DOWNLOADING DATA


# generate a blank cv given an existing table
@application.route("/projects/<application_name>/admin/genblankcsv", methods=['GET', 'POST'])
def genblankcsv(application_name):
    if not user_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)
    DBA = dictionary_of_databases[application_name]
    try:
        return DBA.genBlankCSV(request.form.get("tablename"))
    except Exception as e:
        print(e)

    return redirect("/projects/"+application_name+"/admin/")

# renders the upload form
@application.route("/projects/<application_name>/admin/uploaddata")
def uploaddata(application_name,msg="", err=""):
    if not user_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)
    DBA = dictionary_of_databases[application_name]
    tablenames, columnnames = DBA.getTableAndColumnNames()
    return render_template(templateroute + "upload_table.html",
                           tablenames=tablenames,
                           message=msg,
                           error=err,
                           pname=application_name,
                           username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname())

# adds the data from the CSV to an existing table
@application.route("/projects/<application_name>/admin/uploaddatafrom", methods=['GET', 'POST'])
def uploaddatafrom(application_name):
    if not user_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)
    DBA = dictionary_of_databases[application_name]
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return uploaddata(err="No file part")
        else:
            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                return uploaddata(err="No selected file")
            if file:  # and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                dt = datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S")
                file.save(os.path.join(DBA.uploadfolder, dt + '_' + filename))
                tablename = str(request.form.get("tablename"))

                success, ret = DBA.createTableFrom(os.path.join(DBA.uploadfolder, dt + '_' + filename),
                                                   tablename)
                if success:
                    ret = "Success, data added to table: %s%s%s" % (tablename, "<br/>", ret)
                    return uploaddata(msg=ret)
                else:
                    return uploaddata(err=ret)

    return redirect("/projects/"+application_name+"/admin/")

# creates a new table taking name from form
# if table exists, supplements it with the new data
# todo: check for column missmatch
@application.route("/projects/<application_name>/admin/createtable", methods=['GET', 'POST'])
def createtable(application_name):
    if not user_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)
    DBA = dictionary_of_databases[application_name]
    # create a new table either from scratch or from an existing csv
    tablenames, columnnames = DBA.getTableAndColumnNames()
    success = 0
    ret = ""

    # check for no table name
    if request.form.get("newtablename") == "":
        success = 0
        ret = "Enter table name"

    # check for existing table with this name
    elif request.form.get("newtablename") in tablenames:
        success = 0
        ret = "Table " + request.form.get("newtablename") + " already exists, try a new name"

    # check whether this should be an empty table or from existing data
    elif request.form.get("source") == "emptytable":
        success, ret = DBA.createEmptyTable(request.form.get("newtablename"))

    elif 'file' not in request.files:
        # check if the post request has the file part
        print('No file found')
        success = 0
        ret = "No file part, contact admin"

    else:
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            success = 0
            ret = 'No selected file.'

        elif file:  # and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            dt = datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S")
            file.save(os.path.join(DBA.uploadfolder, dt + '_' + filename))
            success, ret = DBA.createTableFromCSV(os.path.join(DBA.uploadfolder, filename),
                                                  request.form.get("newtablename"))

    if success == 1:
        # todo: this does not work on the fly
        return render_template(templateroute + "create_table.html",
                               tablenames=tablenames, columnnames=columnnames,
                               message="Table " +
                                       request.form.get("newtablename") + " created successfully!\n" + ret,
                               pname=application_name,
                           username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname())
    else:
        return render_template(templateroute + "create_table.html",
                               tablenames=tablenames, columnnames=columnnames,
                               error="Creation of table " + request.form.get("newtablename") +
                                     " failed!<br/>Error: " + ret,
                               pname=application_name,
                           username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname())

# renders the download form
@application.route("/projects/<application_name>/admin/download")
def download(application_name):
    if not user_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)
    DBA = dictionary_of_databases[application_name]
    tablenames, columnnames = DBA.getTableAndColumnNames()

    return render_template(templateroute + "download_table.html",
                           tablenames=tablenames, columnnames=columnnames,
                           pname=application_name,
                           username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname())

# serves the data given the response from the download form
@application.route("/projects/<application_name>/admin/servedata", methods=['GET', 'POST'])
def servedata(application_name):
    if not user_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)
    DBA = dictionary_of_databases[application_name]
    # serves the requested data
    # todo: problems with filename and extension


    try:
        return DBA.serveData(F=request.form,
                             ClassName=str(request.form.get("tablename")))  # os.path.abspath(os.path.dirname(__file__)))
    except Exception as e:
        print(str(e))

    return redirect("/projects/"+application_name+"/admin/")


# endregion










