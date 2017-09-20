#!/usr/bin/python

import sys
import os
from flask import Flask
from flask import render_template, redirect, url_for
from flask import request
import json
path=__file__[0:-9]
sys.path.insert(0,path)

from threading import Lock
from werkzeug.wsgi import pop_path_info, extract_path_info, peek_path_info
from main.sqla.app import create_app, get_user_for_prefix, get_current_schema_id

class PathDispatcher(object):

    def __init__(self, default_app, create_app):
        self.default_app = default_app
        self.create_app = create_app
        self.lock = Lock()
        self.instances = {}

    def get_application(self, prefix):
        with self.lock:
            app = self.instances.get(prefix)
            if app is None:
                app = self.create_app(prefix)
                if app is not None:
                    self.instances[prefix] = app
            return app

    def reload_app(self, prefix):
        print "auto_reloading: "+prefix
        with self.lock:
            app = self.create_app(prefix)
            self.instances[prefix] = app
            return app

    def __call__(self, environ, start_response):
        path_start=peek_path_info(environ)
        mypath=''
        app_blank = self.get_application('')
        if path_start=='projects':
          proj_uri=environ['PATH_INFO']
          uri_parts=proj_uri.split('/')
          mypath=uri_parts[2]
# Erm, that is silly, do this elsewhere!
#        elif path_start=='reload':
#          proj_uri=environ['PATH_INFO']
#          uri_parts=proj_uri.split('/')
#          mypath=uri_parts[2]
#          environ['PATH_INFO']='/projects/'+mypath
#          increment_schema_id(mypath)
        app = self.get_application(mypath)
        if mypath!='':
           if schema_ids[mypath]!=get_current_schema_id(mypath):
              self.reload_app(mypath)
        if app is None:
            app = self.default_app
        return app(environ, start_response)


#from main.web_apps_examples import *

from werkzeug.exceptions import NotFound

schema_ids={}

def make_app(prefix):
    print prefix
    user = get_user_for_prefix(prefix)
    if user is None:
       return NotFound()
    app, schema_id = create_app(user)
    if user!='':
       schema_ids[user]=schema_id
    return app

application = PathDispatcher(NotFound(), make_app)

## from app.sqla import *
#from main.sqla.app import app as application
## application = app
#from main.web_apps_examples import *


