# general database functions which can be used by any database

import sqlalchemy as SqlAl
import csv
from flask import send_file
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import pymysql
import dbconfig

class DBEngine:
    E = SqlAl.null
    metadata = SqlAl.MetaData()

    def __init__(self,db):
        self.metadata = SqlAl.MetaData()
        print(db)
        self.E = SqlAl.create_engine(db)
        self.metadata.bind = self.E

class DatabaseAssistant:
    db=""
    DBE=SqlAl.null

    def __init__(self,db=""):
        self.db = db
        self.DBE = DBEngine(db)

    def resetDB(self,db):
        self.db = db
        self.DBE = DBEngine(db)


    def connect(self, database=""):
        return pymysql.connect(host='localhost',
                               user=dbconfig.db_user,
                               passwd=dbconfig.db_password,
                               db=database)

    def getTableAndColumnNames(self):
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
            print(table.name)
            tablenames.append(table.name)
            thesecolumnnames = []
            for column in table.c:
                thesecolumnnames.append(column.name)
            columnnames.append(thesecolumnnames)

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

    def serveData(self,F,C,p):
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

        self.DBE.metadata.create_all()

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

        if coltype == "Integer":
            # INTEGER or INT
            data_type_formatted = "INTEGER"

        elif coltype == "String":
            # VARCHAR(length)
            data_type_formatted = "VARCHAR("+str(numchar)+")"

        elif coltype == "Characters":
            # CHARACTER[(length)] or CHAR[(length)]
            data_type_formatted = "CHARACTER[("+str(numchar)+")]"

        elif coltype=="Bool":
            # BOOLEAN
            data_type_formatted="BOOLEAN"

        elif coltype=="Time stamp":
            # TIMESTAMP
            data_type_formatted="TIMESTAMP"

        elif coltype=="Date":
            # DATE
            data_type_formatted="DATE"

        elif coltype=="Time":
            # TIME
            data_type_formatted="TIME"

        elif coltype=="Really long string":
            # CLOB[(length)] or CHARACTER
            data_type_formatted = "CLOB[("+str(numchar)+")]"



            # SMALLINT
            # DECIMAL[(p[, s])] or DEC[(p[, s])]
            # NUMERIC[(p[, s])]
            # REAL
            # FLOAT(p)
            # DOUBLE
            # PRECISION
            # LARGE
            # OBJECT[(length)] or CHAR
            # LARGE
            # OBJECT[(length)]
            # BLOB[(length)] or BINARY
            # LARGE
            # OBJECT[(length)]

        query = ("ALTER TABLE "+tablename+" ADD column "+colname+" "+data_type_formatted)

        cursor.execute(query)
        connection.commit()
        connection.close()

