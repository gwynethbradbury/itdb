# general database functions which can be used by any database

import csv
from flask import send_file
import sqlalchemy as SqlAl
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import pymysql
import dbconfig
import pandas as pd
import os


listOfColumnTypesByName = {"Integer":"INTEGER",
                           "String":"VARCHAR",
                           "Characters":"CHARACTER",
                           "Bool":"BOOLEAN",
                           "Time stamp":"TIMESTAMP",
                           "Date":"DATE",
                           "Time":"TIME",
                           "Really long string":"CLOB",
                           "Small integer":"SMALLINT",
                           "Real":"REAL",
                           "Float":"FLOAT",
                           "Double":"DOUBLE",
                           "Precision":"PRECISION",
                           "Text block":"TEXT"}
DataTypeNeedsN= {"INTEGER":False,
                 "VARCHAR":True,
                 "CHARACTER":True,
                 "BOOLEAN":False,
                 "TIMESTAMP":False,
                 "DATE":False,
                 "TIME":False,
                 "CLOB":True,
                 "SMALLINT":False,
                 "REAL":False,
                 "FLOAT":True,
                 "DOUBLE":False,
                 "PRECISION":False,
                 "TEXT":False}
listOfColumnTypesByDescriptor = dict(reversed(item) for item in listOfColumnTypesByName.items())

def desc2formattedtype(coltype,numchar):

    data_type_formatted = listOfColumnTypesByName[coltype]
    if DataTypeNeedsN[listOfColumnTypesByName[coltype]]:
        data_type_formatted = "{}({})".format(data_type_formatted,str(numchar))

    return data_type_formatted



class DBEngine:
    E = SqlAl.null
    metadata = SqlAl.MetaData()
    db=""

    def __init__(self,db):
        self.metadata = SqlAl.MetaData()
        self.db=db
        self.E = SqlAl.create_engine(db)
        self.metadata.bind = self.E


class DatabaseAssistant:
    db = ""
    dbkey=""
    DBE = SqlAl.null
    mydatabasename=""
    adminroute = ""
    approute = ""
    upload_folder=""
    list_template = ""
    detail_template = ""

    filters={}

    def __init__(self,db="",dbkey="",dbname="", upload_folder=""):
        self.db = db
        self.DBE = DBEngine(db)
        self.dbkey=dbkey
        self.mydatabasename = dbname

        self.adminroute = "/projects/" + dbname + "/admin/"
        self.approute = "/projects/" + dbname + "/"

        self.list_template = 'projects/project_listview.html',
        self.detail_template = 'projects/project_detailview.html',
        self.upload_folder=upload_folder

    def resetDB(self,db):
        self.db = db
        self.DBE = DBEngine(db)

    # Gets the database connection
    def connect(self):
        return pymysql.connect(host='localhost',
                               user=dbconfig.db_user,
                               passwd=dbconfig.db_password,
                               db=self.mydatabasename)

    # creates a class from a table
    def classFromTableName(self, classname, fields, classes_loaded=True):
        if classes_loaded:
            from main.sqla.classes import initialise_single_class
            C = initialise_single_class(self.mydatabasename,classname)
        else:

            import importlib

            # my_module = importlib.import_module('app.classes.'+classname)
            # from app.classes import classdict
            # C = classdict["cls{}{}".format(tablename,classname)]


            from sqlalchemy.ext.declarative import declarative_base

            mydict = {'__tablename__': classname,
                      '__table_args__': ({'autoload': True},),
                      '__bind_key__': self.dbkey,}

            Base = declarative_base(self.DBE.E)
            C = type(classname, (Base,), mydict)

            # if classname=="comment":
            #     from flask_sqlalchemy import SQLAlchemy
            #     from .. import db
            #     # db = SQLAlchemy(app)
            #     fields2=['Article','user','comment']
            #     news = self.classFromTableName('news',fields2)
            #     from app.admin.models import news as news
            #     try:
            #         C.news = db.relationship('news', backref=db.backref('comments',
            #                                                           lazy='dynamic'))
            #     except Exception as e:
            #         print(e)

        C.metadata = C.__table__.metadata
        C.fields=fields
        C.__str__ = "hi"
        return C


    # region RETRIEVE DATA FROM/ABOUT THE DATABASE
    #

    # gets the table and respective column names from the database
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
            if not(table.name[0]=='x' and table.name[1]=='_'):
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

    # gets data from the table given a list of desired fields
    def retrieveDataFromDatabase(self, classname, columnnames,classes_loaded= True):

        C = self.classFromTableName(classname, columnnames, classes_loaded=classes_loaded)

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

    # serves the data to the client
    def serveData(self,F,ClassName):
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


        exportpath = self.upload_folder + '/export.csv'
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

    # endregion


    # region EDIT THE EXISTING DATA/TABLES
    #

    # adds a column to the database
    def addColumn(self,tablename,colname="test",coltype="Integer",numchar=100):
        msg=""
        print("attempting to add column "+colname+" ("+coltype+") to table "+tablename+"...")
        try:
            mytable = SqlAl.Table(tablename, self.DBE.metadata, autoload=True)  # .data, metadata, autoload=True)
        except Exception as e:
            print(str(e))
            msg = ("couldn't get table "+tablename+", stopping")



        tablenames, columnnames = self.getTableAndColumnNames()
        i=0
        for t in tablenames:
            if t==tablename:
                for cc in columnnames[i]:
                    if cc==colname:
                        msg=(colname +" already exists in table.")
                        print(msg)
                        return msg, 0
            i += 1

        data_type_formatted = desc2formattedtype(coltype,numchar)


        # self.DBE.E.execute("ALTER TABLE "+tablename+" ADD column "+colname+" "+data_type_formatted+";")

        try:
            connection = self.connect()
            query = "ALTER TABLE {} ADD COLUMN {} {};".format(tablename,colname,data_type_formatted)
            with connection.cursor() as cursor:
                cursor.execute(query)
            for c in cursor:
                topic = c[0]
        except Exception as e:
            print(e)
        finally:
            connection.close

        return msg, 1

    # removes a column from the database
    def remColumn(self,tablename, colname):
        msg=""
        print("attempting to remove column " + colname + " from table "+tablename+"...")
        try:
            mytable = SqlAl.Table(tablename, self.DBE.metadata, autoload=True)  # .data, metadata, autoload=True)
        except Exception as e:
            print(str(e))
            return ("couldn't get table "+tablename+", stopping"), 0



        tablenames, columnnames = self.getTableAndColumnNames(tablename)
        if not colname in columnnames[0]:
            return "failed, could not find column in table {}".format(tablename), 0

        try:
            connection = self.connect()
            query = "ALTER TABLE {} DROP COLUMN {};".format(tablename,colname)
            with connection.cursor() as cursor:
                cursor.execute(query)
        except Exception as e:
            print(e)
        finally:
            connection.close

        return msg, 1

    # adds a primary key column for integer ids to the table
    def addIdColumn(self, table_name, column_name="id"):
        self.DBE.E.execute('ALTER TABLE %s ADD %s INT PRIMARY KEY AUTO_INCREMENT;' %(table_name, column_name))

    # changes the name of a column
    def changeColumnName(self, tablename, fromcolumn, tocolumn):
        self.DBE.E.execute('ALTER TABLE %s CHANGE %s %s INTEGER;' %(tablename, fromcolumn, tocolumn))

    # renames a table
    def renameTable(self, fromtablename, totablename):
        self.DBE.E.execute('ALTER TABLE %s RENAME TO %s;' % (fromtablename, totablename))

    # clears all entries from a table without deleting it
    def clearTable(self,tablename):
        self.DBE.E.execute("DELETE FROM %s;" % (tablename))

    # deletes specidied table
    def deleteTable(self,tablename):
        # self.renameTable(tablename,'x_'+tablename)
        self.DBE.E.execute('DROP TABLE %s;' %(tablename))

        # tn,cn=self.getTableAndColumnNames(tablename)
        # C = self.classFromTableName(str(tablename),cn[0])
        # for table in self.DBE.metadata.tables.values():
        #     if tablename==table.name:
        #         C.__table__.drop(self.DBE.E)
        #         return

    # endregion

    # region UPLOADING TABLES, APPENDING TO TABLES, CREATING NEW TABLES
    #

    def createTableFrom(self, filepath, tablename):
        filename, file_extension = os.path.splitext(filepath)

        if file_extension.lower()=='.csv':
            success, msg = self.createTableFromCSV(filepath,tablename)
        elif file_extension.lower()=='.xls' or file_extension.lower()=='.xlsx':
            success, msg = self.createTableFromXLS(filepath,tablename)

        return success, msg

    # creates a new table from a csv file
    def createTableFromCSV(self, filepath, tablename):

        df = pd.read_csv(filepath,parse_dates=True)

        try:
            msg=""

            cnames = df.columns.values.tolist()
            if 'id' in cnames:
                df = df.rename(columns={'id': 'imported_id'})
                msg="Warning: integer id column found. Primary key column has been created and id" \
                    "column has changed to 'imported_id'"

            df.to_sql(tablename,
                      self.DBE.E,
                      if_exists='append',
                      index=False,chunksize=50)


            t,c = self.getTableAndColumnNames(tablename=tablename)

            print "found columns:"
            print(c)
            if not('id' in c[0]):
                self.addIdColumn(tablename, 'id')
            # for cc in c[0]:
            #     if cc=='id':
            #         self.changeColumnName(tablename,'id','imported_id')
            #         msg="Warning: integer id column found. Primary key column has been created and id" \
            #             "column has changed to 'imported_id'"


            return 1,msg

        except Exception as e:
            print(str(e))
            return 0,("something went wrong - maybe table exists and columns are mismatched?")

    # creates a new table from a xls file
    def createTableFromXLS(self, filepath, tablename):

        df = pd.read_excel(filepath,
                           sheetname=tablename,
                           parse_dates=True)

        try:
            msg=""

            cnames = df.columns.values.tolist()
            if 'id' in cnames:
                df = df.rename(columns={'id': 'imported_id'})
                msg="Warning: integer id column found. Primary key column has been created and id" \
                    "column has changed to 'imported_id'"

            df.to_sql(tablename,
                      self.DBE.E,
                      if_exists='append',
                      index=False,chunksize=50)


            t,c = self.getTableAndColumnNames(tablename=tablename)

            print "found columns:"
            print(c)
            if not('id' in c[0]):
                self.addIdColumn(tablename, 'id')
            # for cc in c[0]:
            #     if cc=='id':
            #         self.changeColumnName(tablename,'id','imported_id')
            #         msg="Warning: integer id column found. Primary key column has been created and id" \
            #             "column has changed to 'imported_id'"


            return 1,msg

        except Exception as e:
            print(str(e))
            return 0,("something went wrong - maybe table exists and columns are mismatched?")

    # generates a template csv for uploading data to an existing table
    def genBlankCSV(self, tablename=""):
        # generates an empty file to upload data for the selected table


        db_connection = self.DBE.E.connect()
        mytable = SqlAl.Table(tablename, self.DBE.metadata, autoload=True)  # .data, metadata, autoload=True)
        print("1")
        select = SqlAl.sql.select([mytable])
        print("2")
        result = db_connection.execute(select)

        exportpath = self.upload_folder + 'upload.csv'
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

    # creates a new empty table
    def createEmptyTable(self,tn):
        if tn[0]=='x' and tn[1]=='_':
            return 0,"invalid tablename"
        tablenames, columnnames = self.getTableAndColumnNames()
        if tablenames.__len__()>0:
            for t in tablenames:
                if t==tn:
                    return 0,(tn + " already exists, stopping")



        new_table = Table(tn, self.DBE.metadata,
                          Column('id', Integer, primary_key=True))

        self.DBE.metadata.create_all(bind=self.DBE.E, tables=[new_table])
        return 1,""

    # endregion



    # executes a custom query
    #todo: complete this. not safe
    def customQuery(self, querystring):
        self.DBE.E.execute(querystring)



