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

class PathDispatcher(object):

    def __init__(self, default_app, create_app):
        self.default_app = default_app
        self.create_app = create_app
        self.lock = Lock()
        self.instances = {}

    def get_application(self, prefix):
        print "ga_Prefix: "+prefix
        with self.lock:
            app = self.instances.get(prefix)
            if app is None:
                app = self.create_app(prefix)
                if app is not None:
                    self.instances[prefix] = app
            return app

    def __call__(self, environ, start_response):
        path_start=peek_path_info(environ)
        print "Prefix: path_start: "+path_start
        mypath=path_start
        print "Prefix: mypath: "+mypath
        if path_start=='projects':
          print "Prefix: in project mypath: "+mypath
          proj_uri=environ['PATH_INFO']
          print "Prefix: in project projiri: "+proj_uri
          uri_parts=proj_uri.split('/')
          mypath=uri_parts[2]
        app = self.get_application(mypath)
        if app is None:
            app = self.default_app
        return app(environ, start_response)


from main.sqla.app import create_app, get_user_for_prefix
#from main.web_apps_examples import *

from werkzeug.exceptions import NotFound


def make_app(prefix):
    print prefix
    user = get_user_for_prefix(prefix)
    if user is None:
       return NotFound()
    return create_app(user)

application = PathDispatcher(NotFound(), make_app)

## from app.sqla import *
#from main.sqla.app import app as application
## application = app
#from main.web_apps_examples import *


