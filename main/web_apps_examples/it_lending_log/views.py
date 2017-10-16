# from ...sqla.app import app as map
from main.auth.iaasldap import LDAPUser as iaasldap
iaasldap = iaasldap()
# from .models import pages


# from . import uploadfolder

# if dbconfig.test:
#     from mockdbhelper import MockDBHelper as DBHelper
# else:
from dbhelper import DBHelper



from main.sqla.dev import *


def assignroutes(application):
    approute = "/projects/it_lending_log/app/"
    shortapproute = "/it_lending_log/"
    templateroute = "projects/it_lending_log/"
    dbbb = 'mysql+pymysql://{}:{}@localhost/{}'.format(dbconfig.db_user,
                                                       dbconfig.db_password,
                                                       'it_lending_log')#map.name)
    # db2 = dataset.connect(dbbb, row_type=pages)
    dbbindkey="project_online_learning_db"
    appname="it_lending_log"
    DBA = DatabaseAssistant(dbbb,dbbindkey,appname)
    projects = []
    DB = DBHelper("it_lending_log")#map.name)


    @application.route(approute)
    @application.route(shortapproute)
    def it_lending_log():
        items = []
        log=[]
        fields = ['id','item', 'date_out', 'returned', 'borrower', 'signed_out_by', 'comment']

        try:
            items = DB.getAllItems()
            logs = DB.getAllLogs()

            # projects = DB.get_all_projects()
            # projects = json.dumps(projects)
            return render_template(templateroute+"it_lending_log"+".html",
                                   itemlist=items,
                                   log=logs,
                                   fields=fields,
                                   username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                                   servicelist=iaasldap.get_groups())
        except Exception as e:
            print e
            data = []
        # print(data)
        return render_template(templateroute+"it_lending_log"+".html",
                               log=log,
                               fields=fields,
                               itemlist=items,
                               username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                               servicelist=iaasldap.get_groups())

    @application.route(approute+"submitentry", methods=['GET', 'POST'])
    @application.route(shortapproute+"submitentry", methods=['GET', 'POST'])
    def it_lending_log_submit():
        try:
            # fields = ['id', 'item', 'date_out', 'returned', 'borrower', 'signed_out_by', 'comment']

            item = request.form.get("item")
            date_out = request.form.get("date_out")
            returned = (request.form.get("returned")=='on')
            borrower = request.form.get("borrower")
            signed_out_by = request.form.get("signed_out_by")
            comment = request.form.get("comment")
            DB.addEntry(item, date_out, returned, borrower, signed_out_by, comment)
        except Exception as e:
            print e
        # home()
        return redirect(approute)#url_for("map"+"_app."+"map"))

    @application.route(approute+"submititem", methods=['GET', 'POST'])
    @application.route(shortapproute+"submititem", methods=['GET', 'POST'])
    def it_lending_item_submit():
        try:
            # fields = ['id', 'item', 'date_out', 'returned', 'borrower', 'signed_out_by', 'comment']

            name = request.form.get("name")
            comment = request.form.get("comment")
            DB.addItem(name, comment)
        except Exception as e:
            print e
        # home()
        return redirect(approute)#url_for("map"+"_app."+"map"))

    @application.route(approute+"deleteitem/<table>/<id>")
    @application.route(shortapproute+"deleteitem/<table>/<id>")
    def it_lending_log_delete_item(table,id):
        try:
            DB.removeItem(table,id)
        except Exception as e:
            print e

        return redirect(approute)

    @application.route(approute+"markreturned/<id>")
    @application.route(shortapproute+"markreturned/<id>")
    def it_lending_log_return_item(id):
        try:
            DB.returnItem(id)
        except Exception as e:
            print e

        return redirect(approute)

    @application.route(approute+"alter/<id>", methods=['GET','POST'])
    @application.route(shortapproute+"alter/<id>", methods=['GET','POST'])
    def it_lending_log_alter_log(id):

        if request.method == 'POST':
            try:
                # fields = ['id', 'item', 'date_out', 'returned', 'borrower', 'signed_out_by', 'comment']

                item = request.form.get("item")
                date_out = request.form.get("date_out")
                returned = (request.form.get("returned") == 'on')
                borrower = request.form.get("borrower")
                signed_out_by = request.form.get("signed_out_by")
                comment = request.form.get("comment")
                DB.alterLog(id, item, date_out, returned, borrower, signed_out_by, comment)
            except Exception as e:
                print e
        else:
            try:
                items = DB.getAllItems()
                logitem = DB.getLog(id)
                logitem=logitem[0]
                return render_template(templateroute+"alterlog"+".html",
                                       itemlist=items,
                                       logitem=logitem,
                                       username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                                       servicelist=iaasldap.get_groups())
            except Exception as e:
                print e

        return redirect(approute)

    @application.route(approute+"alter/item/<id>", methods=['GET','POST'])
    @application.route(shortapproute+"alter/item/<id>", methods=['GET','POST'])
    def it_lending_log_alter_item(id):

        if request.method == 'POST':
            try:

                name = request.form.get("name")
                comment = request.form.get("comment")
                DB.alterItem(id, name, comment)

            except Exception as e:
                print e
        else:
            try:
                items = DB.getAllItems()
                thisitem = DB.getItem(id)
                thisitem=thisitem[0]
                return render_template(templateroute+"alteritem"+".html",
                                       itemlist=items,
                                       thisitem=thisitem,
                                       username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                                       servicelist=iaasldap.get_groups())
            except Exception as e:
                print e

        return redirect(approute)


# # assignadminroutes(map)