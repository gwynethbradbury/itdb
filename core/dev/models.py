# general database functions which can be used by any database

import sqlalchemy as SqlAl
import csv
from flask import send_file
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import pymysql
import dbconfig
import pandas as pd

listOfColumnTypes = ["Integer",
                   "String",
                   "Characters",
                   "Bool",
                   "Time stamp",
                   "Date",
                   "Time",
                   "Really long string",
                   "Small integer",
                   "Real",
                   "Float",
                   "Double",
                   "Precision"]


def desc2formattedtype(coltype,numchar):
    data_type_formatted=""

    if coltype == "Integer":
        # INTEGER or INT
        data_type_formatted = "INTEGER"

    elif coltype == "String":
        # VARCHAR(length)
        data_type_formatted = "VARCHAR(" + str(numchar) + ")"

    elif coltype == "Characters":
        # CHARACTER[(length)] or CHAR[(length)]
        data_type_formatted = "CHARACTER[(" + str(numchar) + ")]"

    elif coltype == "Bool":
        # BOOLEAN
        data_type_formatted = "BOOLEAN"

    elif coltype == "Time stamp":
        # TIMESTAMP
        data_type_formatted = "TIMESTAMP"

    elif coltype == "Date":
        # DATE
        data_type_formatted = "DATE"

    elif coltype == "Time":
        # TIME
        data_type_formatted = "TIME"

    elif coltype == "Really long string":
        # CLOB[(length)] or CHARACTER
        data_type_formatted = "CLOB[(" + str(numchar) + ")]"

    elif coltype=="Small integer":
        # SMALLINT
        data_type_formatted = "SMALLINT"

    elif coltype=="Real":
        # REAL
        data_type_formatted="REAL"

    elif coltype=="Float":
        # FLOAT(p)
        data_type_formatted="FLOAT("+str(numchar)+")"

    elif coltype=="Double":
        # DOUBLE
        data_type_formatted="DOUBLE"

    elif coltype=="Precision":
        # PRECISION
        data_type_formatted="PRECISION"

    return data_type_formatted


class DBEngine:
    E = SqlAl.null
    metadata = SqlAl.MetaData()

    def __init__(self,db):
        self.metadata = SqlAl.MetaData()
        print(db)
        self.E = SqlAl.create_engine(db)
        self.metadata.bind = self.E


class DatabaseAssistant:
    db = ""
    dbkey=""
    DBE = SqlAl.null
    mydatabasename=""

    def __init__(self,db="",dbkey="",dbname=""):
        self.db = db
        self.DBE = DBEngine(db)
        self.dbkey=dbkey
        self.mydatabasename = dbname

    def resetDB(self,db):
        self.db = db
        self.DBE = DBEngine(db)


    def connect(self):
        return pymysql.connect(host='localhost',
                               user=dbconfig.db_user,
                               passwd=dbconfig.db_password,
                               db=self.mydatabasename)

    def getTableAndColumnNames(self, tablename=""):
        # gets the table and column names given a db link

        columnnames = []
        tablenames = []

        # tablenames.append('other')
        # thesecolumnnames2 = []
        # for i in range(3):
        #     thesecolumnnames2.append(str(i))
        # columnnames.append(thesecolumnnames2)

        self.DBE.metadata.reflect(self.DBE.E)
        for table in self.DBE.metadata.tables.values():
            if table.name==tablename or tablename=="":
                print(table.name)
                tablenames.append(table.name)
                thesecolumnnames = []
                for column in table.c:
                    thesecolumnnames.append(column.name)
                columnnames.append(thesecolumnnames)
            if table.name==tablename:
                return tablenames,columnnames

        print tablenames
        print columnnames

        return tablenames,columnnames

    def genBlankCSV(self, tablename="", p=""):
        # generates an empty file to upload data for the selected table

        mytable = SqlAl.Table(tablename, self.DBE.metadata, autoload=True)  # .data, metadata, autoload=True)

        db_connection = self.DBE.E.connect()
        print("1")
        select = SqlAl.sql.select([mytable])
        print("2")
        result = db_connection.execute(select)

        exportpath = p + '/data/upload.csv'
        fh = open(exportpath, 'wb')
        outcsv = csv.writer(fh)

        outcsv.writerow(result.keys())
        # outcsv.writerows(result)

        fh.close()

        try:
            # return
            return send_file(exportpath,
                             attachment_filename='export.csv')
        except Exception as e:
            print(str(e))

        return

    def retrieveDataFromDatabase(self, classname, columnnames):

        C = self.classFromTableName(classname, columnnames)

        # retrieves the selected columns

        Session = sessionmaker(bind=self.DBE.E)

        self.DBE.E.echo = False  # Try changing this to True and see what happens

        session = Session()

        col_names_str = columnnames
        columns = [column(col) for col in col_names_str]

        q = select(from_obj=C, columns=columns)
        result = session.execute(q)

        KEYS = result.keys()
        print(KEYS)
        result_as_string = []
        for row in result:
            rr = []
            for i in row:
                rr.append(str(i))
            result_as_string.append(rr)


        return result, result_as_string

    def serveData(self,F,ClassName,p):
        # serves the data from the database given the corresponding class C

        t = F.get("tablename")
        w = F.get("wholetable")
        print('Download requested for table="%s"' %
              t)

        if w:
            print('yes')
        else:
            print('no')
            #
        #

        mytable = Table(t, self.DBE.metadata, autoload=True)

        columnnames = []

        for cc in mytable.c:
            if w:
                columnnames.append(cc.name)
            elif F.get(t + "_" + cc.name):
                columnnames.append(cc.name)

        result, result_as_string = self.retrieveDataFromDatabase(ClassName, columnnames)


        exportpath = p + '/data/export.csv'
        fh = open(exportpath, 'wb')
        outcsv = csv.writer(fh)

        outcsv.writerow(result.keys())
        outcsv.writerows(result_as_string)

        fh.close()

        try:
            return send_file(exportpath,
                             attachment_filename='export.csv')
        except Exception as e:
            print(str(e))

    def createEmptyTable(self,tn):
        tablenames, columnnames = self.getTableAndColumnNames()
        if tablenames.__len__()>0:
            for t in tablenames:
                if t==tn:
                    print(tn + " already exists, stopping")
                    return


        new_table = Table(tn, self.DBE.metadata,
                          Column('id', Integer, primary_key=True))

        self.DBE.metadata.create_all(bind=self.DBE.E, tables=[new_table])



    def addColumn(self,tablename,colname="test",coltype="Integer",numchar=100):
        print("attempting to add column "+colname+" ("+coltype+") to table "+tablename+"...")
        try:
            mytable = SqlAl.Table(tablename, self.DBE.metadata, autoload=True)  # .data, metadata, autoload=True)
        except Exception as e:
            print(str(e))
            print("couldn't get table "+tablename+", stopping")



        tablenames, columnnames = self.getTableAndColumnNames()
        i=0
        for t in tablenames:
            if t==tablename:
                for cc in columnnames[i]:
                    if cc==colname:
                        print(colname +" already exists in table, stopping.")
                        return
            i += 1


        connection = self.connect("map")
        cursor = connection.cursor()

        data_type_formatted = desc2formattedtype(coltype,numchar)

        query = ("ALTER TABLE "+tablename+" ADD column "+colname+" "+data_type_formatted)

        cursor.execute(query)
        connection.commit()
        connection.close()

    def addIdColumn(self, table_name, column_name="id"):
        self.DBE.E.execute('ALTER TABLE %s ADD %s INT PRIMARY KEY AUTO_INCREMENT' %(table_name, column_name))

    def changeColumnName(self, tablename, fromcolumn, tocolumn):
        self.DBE.E.execute('ALTER TABLE %s CHANGE %s %s INTEGER' %(tablename, fromcolumn, tocolumn))

    def createTableFromCSV(self, filepath, tablename):


        df = pd.read_csv(filepath,parse_dates=True)

        try:
            df.to_sql(tablename,
                      self.DBE.E,
                      if_exists='append',
                      index=False,chunksize=50)

            # column = Column('new column', Integer, primary_key=True)
            t,c = self.getTableAndColumnNames(tablename=tablename)
            column_name='id'
            print "found columns:"
            print(c)
            for cc in c[0]:
                if cc=='id':
                    self.changeColumnName(tablename,'id','imported_id')

            self.addIdColumn(tablename, column_name)

        except Exception as e:
            print(str(e))
            print("something went wrong - maybe table exists and columns are mismatched?")

    def classFromTableName(self, classname, fields):
        mydict = {'__tablename__': classname,
                  '__table_args__': {'autoload': True},
                  '__bind_key__': self.dbkey,}

        from sqlalchemy.ext.declarative import declarative_base

        Base = declarative_base(self.DBE.E)
        C = type(classname, (Base,), mydict)
        C.fields=fields
        return C




from flask import Blueprint, request, g, redirect, url_for, abort, \
    render_template
from flask.views import MethodView
from wtforms.ext.sqlalchemy.orm import model_form

class CRUDView2(MethodView):
    list_template = 'admin/listview.html'
    detail_template = 'admin/detailview.html'
    DBA = SqlAl.null
    sesh = SqlAl.null

    def __init__(self, model, endpoint, appname, dbbindkey, list_template=None,
                 detail_template=None, exclude=None, filters=None):
        self.model = model
        self.endpoint = endpoint

        self.DBA = DatabaseAssistant('mysql+pymysql://{}:{}@localhost/{}'.format(dbconfig.db_user, dbconfig.db_password,appname),
                                     dbbindkey,
                                     appname)
        # so we can generate a url relevant to this
        # endpoint, for example if we utilize this CRUD object
        # to enpoint comments the path generated will be
        # /admin/comments/
        self.path = url_for('.%s' % self.endpoint)
        if list_template:
            self.list_template = list_template
        if detail_template:
            self.detail_template = detail_template
        self.filters = filters or {}
        sesh = sessionmaker(bind=self.DBA.DBE.E)
        self.sesh = sesh()
        self.ObjForm = model_form(self.model, self.sesh, exclude=exclude)

    def render_detail(self, **kwargs):
        return render_template(self.detail_template, path=self.path, **kwargs)

    def render_list(self, fields, **kwargs):
        return render_template(self.list_template, path=self.path,
                               fields=fields,
                               filters=self.filters, **kwargs)

    def get(self, obj_id='', operation='', filter_name=''):
        if operation == 'new':
            #  we just want an empty form
            form = self.ObjForm()
            action = self.path
            return self.render_detail(form=form, action=action)

        if operation == 'delete':
            # works, given id from form but that bit is incorrect
            obj = self.sesh.query(self.model).filter_by(id=obj_id).first()
            self.sesh.delete(obj)
            self.sesh.commit()

        # list view with filter
        if operation == 'filter':
            func = self.filters.get(filter_name)
            obj = func(self.model)
            return self.render_list(obj=obj, fields=obj.fields, filter_name=filter_name)

        if obj_id:
            # this creates the form fields base on the model
            # so we don't have to do them one by one
            ObjForm = model_form(self.model, self.sesh)

            obj = self.sesh.query(self.model).filter_by(id=obj_id).first()
            # populate the form with our blog data
            form = self.ObjForm(obj=obj)
            # action is the url that we will later use
            # to do post, the same url with obj_id in this case
            action = request.path
            return self.render_detail(form=form, action=action)

        q = select(from_obj=self.model, columns=['*'])
        result = self.sesh.execute(q)

        KEYS = result.keys()
        obj=[]
        for r in result:
            obj.append(r)
        return self.render_list(obj=obj,fields=KEYS)

    def post(self, obj_id=''):
        # either load and object to update if obj_id is given
        # else initiate a new object, this will be helpfull
        # when we want to create a new object instead of just
        # editing existing one
        if obj_id:
            obj = self.sesh.query(self.model).filter_by(id=obj_id).first()
        else:
            obj = self.model()

        ObjForm = model_form(self.model, self.sesh)
        # populate the form with the request data
        form = self.ObjForm(request.form)
        # this actually populates the obj (the blog post)
        # from the form, that we have populated from the request post
        form.populate_obj(obj)

        # db.session.add(obj)
        self.sesh.add(obj)
        self.sesh.commit()

        return redirect(self.path)
        # pass



def register_crud2(app, url, endpoint, model, dbbindkey, appname, decorators=[], **kwargs):
    view = CRUDView2.as_view(endpoint,dbbindkey, appname, endpoint=endpoint,
                            model=model, **kwargs)

    for decorator in decorators:
        view = decorator(view)

    app.add_url_rule('%s/' % url, view_func=view, methods=['GET', 'POST'])
    app.add_url_rule('%s/<int:obj_id>/' % url, view_func=view)
    app.add_url_rule('%s/<operation>/' % url, view_func=view, methods=['GET'])
    app.add_url_rule('%s/<operation>/<int:obj_id>/' % url, view_func=view,
                     methods=['GET'])
    app.add_url_rule('%s/<operation>/<filter_name>/' % url, view_func=view,
                     methods=['GET'])
    print('registered crud at ' + url)