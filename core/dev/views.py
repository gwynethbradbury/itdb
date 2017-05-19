from core.dev import *


def assignAdminRoutesForDatabase(application, DBA, upload_folder):
    adminroute = "/projects/" + application.name + "/admin/"
    approute = "/projects/" + application.name + "/"
    list_template = 'projects/' + application.name + '/listview.html',
    detail_template = 'projects/' + application.name + '/detailview.html',
    filters={}
    uploadfolder = upload_folder#dir_path = os.path.dirname(os.path.realpath(__file__)) + '/data/'

    def render_detail(tablename, **kwargs):
        t, c = DBA.getTableAndColumnNames()
        path = "%s%s/" % (adminroute, tablename)  # url_for('.%s' % tablename)
        return render_template(detail_template, path=path,
                               tablenames=t,
                               **kwargs)

    def render_list(tablename, fields, **kwargs):
        t, c = DBA.getTableAndColumnNames()
        path = "%s%s/" % (adminroute, tablename)  # url_for('.%s' % tablename)
        return render_template(list_template, path=path,
                               fields=fields,
                               tablenames=t,
                               tablename=tablename,
                               filters=filters,
                               **kwargs)


    ##########PATHS###########

    # VIEWING DATA

    # list the databases
    @application.route("/projects/"+application.name+"/admin/")
    def showtables():
        tablenames, columnnames = DBA.getTableAndColumnNames()

        print("tablenames are:")
        print(tablenames)
        print("end")
        return render_template(approute+application.name+"admin.html",
                               tablenames=tablenames)

    # show the list vew for a given table in the DB
    @application.route("/projects/" + application.name + "/admin/<tablename>/")
    def showTable(tablename):
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

            return render_list(tablename=tablename, obj=obj, fields=KEYS)
        except Exception as e:
            print(e)

        return redirect(adminroute)

    # Show the detail view for a given entry in a given table
    @application.route("/projects/"+application.name+"/admin/<tablename>/<obj_id>")
    def displayObject(tablename,obj_id):

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
            return render_detail(tablename=tablename,form=form, action=action)

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
        return render_detail(form=form, action=action)

    # apply a filter to the list view for a table
    @application.route("/projects/" + application.name + "/admin/<tablename>/filter/<filter_name>")
    def filterObjects(tablename, filter_name):
        tns,cns = DBA.getTableAndColumnNames(tablename=tablename)
        model = DBA.classFromTableName(classname=str(tablename),fields=cns[0])

        func = filters.get(filter_name)
        obj = func(model)

        return render_list(tablename=tablename, obj=obj, fields=obj.fields, filter_name=filter_name)
        pass

    # EDITING TABLES

    # creating a new table
    @application.route(adminroute+"newtable")
    def newtable():

        tablenames,columnnames=DBA.getTableAndColumnNames()

        return render_template(approute+"create_table.html",
                               tablenames=tablenames,columnnames=columnnames)

    # adding a column to an existing table
    # todo: unfinished
    @application.route(adminroute+"addcolumn")
    def addcolumn():

        tablenames, columnnames = DBA.getTableAndColumnNames()

        DBA.addColumn("newtable", "test2","Time stamp")

        return render_template(approute+"create_table.html",
                               tablenames=tablenames,columnnames=columnnames)

    # delete a whole table
    @application.route(adminroute+"deletetable/<page>")
    def deletetable(page):
        DBA.deleteTable(page)
        # DBA.DBE.refresh()
        return redirect(adminroute)

    # clear all entries from a table
    @application.route(adminroute+"cleartable/<page>")
    def cleartable(page):
        DBA.clearTable(page)
        return redirect(adminroute)



    # EDITING AND CREATING AN ITEM

    # Generate the form for creating a new item
    @application.route("/projects/" + application.name + "/admin/<tablename>/new")
    def newObjectForm(tablename):
        tns, cns = DBA.getTableAndColumnNames(tablename=tablename)
        model = DBA.classFromTableName(classname=str(tablename), fields=cns[0])
        sesh = sessionmaker(bind=DBA.DBE.E)
        sesh = sesh()

        path = "%s%s/" %(adminroute,tablename)#url_for('.%s' % tablename)
        ObjForm = model_form(model, sesh, exclude=None)
        #  we just want an empty form
        form = ObjForm()
        action = "%s" %("createnew")
        return render_detail(tablename=tablename, form=form, action=action)

    # create the item based on the class and form responses
    @application.route("/projects/" + application.name + "/admin/<tablename>/createnew",
                       methods=['GET', 'POST'])
    def createnew(tablename, obj_id=''):
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

        path = "%s%s/" %(adminroute,tablename)#url_for('.%s' % tablename)
        return redirect(path)

    # delete an item
    @application.route("/projects/"+application.name+"/admin/<tablename>/delete/<id>/")
    def deleteObject(tablename,id):
        tns,cns = DBA.getTableAndColumnNames(tablename=tablename)
        model = DBA.classFromTableName(classname=str(tablename),fields=cns[0])

        sesh = sessionmaker(bind=DBA.DBE.E)
        sesh = sesh()
        # ObjForm = model_form(model, sesh, exclude=None)

        obj = sesh.query(model).filter_by(id=id).first()
        sesh.delete(obj)
        sesh.commit()

        q = select(from_obj=model, columns=['*'])
        result = sesh.execute(q)

        KEYS = result.keys()
        obj=[]
        for r in result:
            obj.append(r)

        return render_list(tablename=tablename,obj=obj,fields=KEYS)


    # UPLOADING AND DOWNLOADING DATA


    # generate a blank cv given an existing table
    @application.route(adminroute+"genblankcsv", methods=['GET', 'POST'])
    def genblankcsv():
        try:
            return DBA.genBlankCSV(request.form.get("tablename"),
                                   p=uploadfolder)
        except Exception as e:
            print(e)

        return redirect(adminroute)

    # renders the upload form
    @application.route(adminroute+"uploaddata")
    def uploaddata(msg="", err=""):
        tablenames, columnnames = DBA.getTableAndColumnNames()
        return render_template(approute+"upload_table.html",
                               tablenames=tablenames,
                               message=msg,
                               error=err)

    # adds the data from the CSV to an existing table
    @application.route(adminroute+"uploaddatafrom", methods=['GET', 'POST'])
    def uploaddatafrom():
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                return uploaddata( err="No file part")
            else:
                file = request.files['file']
                # if user does not select file, browser also
                # submit a empty part without filename
                if file.filename == '':
                    return uploaddata( err="No selected file")
                if file:# and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    dt = datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S")
                    file.save(os.path.join(uploadfolder, dt+'_'+filename))
                    tablename = str(request.form.get("tablename"))

                    success, ret = DBA.createTableFrom(os.path.join(uploadfolder, dt+'_'+filename),
                                                       tablename)
                    if success:
                        ret = "Success, data added to table: %s%s%s" %(tablename,"<br/>",ret)
                        return uploaddata(msg=ret)
                    else:
                        return uploaddata(err=ret)

        return redirect(adminroute)

    # creates a new table taking name from form
    # if table exists, supplements it with the new data
    # todo: check for column missmatch
    @application.route(adminroute+"createtable", methods=['GET', 'POST'])
    def createtable():
        #create a new table either from scratch or from an existing csv
        tablenames, columnnames = DBA.getTableAndColumnNames()
        success=0
        ret=""

        #check for no table name
        if request.form.get("newtablename")=="":
            success=0
            ret="Enter table name"

        #check for existing table with this name
        elif request.form.get("newtablename") in tablenames:
            success=0
            ret="Table "+request.form.get("newtablename")+" already exists, try a new name"

        #check whether this should be an empty table or from existing data
        elif request.form.get("source") == "emptytable":
            success, ret = DBA.createEmptyTable(request.form.get("newtablename"))

        elif 'file' not in request.files:
            # check if the post request has the file part
            print('No file found')
            success=0
            ret="No file part, contact admin"

        else:
            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                success=0
                ret = 'No selected file.'

            elif file:  # and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                dt = datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S")
                file.save(os.path.join(uploadfolder, dt + '_' + filename))
                success, ret = DBA.createTableFromCSV(os.path.join(uploadfolder, filename),
                                                      request.form.get("newtablename"))

        if success==1:
            # todo: this does not work on the fly
            return render_template(approute+"create_table.html",
                                   tablenames=tablenames, columnnames=columnnames,
                                   message="Table " +
                                           request.form.get("newtablename") + " created successfully!\n" + ret)
        else:
            return render_template(approute+"create_table.html",
                                   tablenames=tablenames, columnnames=columnnames,
                                   error="Creation of table " + request.form.get("newtablename") +
                                           " failed!<br/>Error: "+ret)


    # renders the download form
    @application.route(adminroute+"download")
    def download():
        tablenames, columnnames = DBA.getTableAndColumnNames()

        return render_template(approute+"download_table.html",
                               tablenames=tablenames,columnnames=columnnames)

    # serves the data given the response from the download form
    @application.route(adminroute+"servedata", methods=['GET', 'POST'])
    def servedata():
        #serves the requested data
        # todo: problems with filename and extension


        try:
            return DBA.serveData(F=request.form,
                                 ClassName=str(request.form.get("tablename")),
                                 p=uploadfolder)#os.path.abspath(os.path.dirname(__file__)))
        except Exception as e:
            print( str(e))

        return redirect(adminroute)