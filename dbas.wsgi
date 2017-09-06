#!/usr/bin/python

import sys
import os
from flask import Flask
from flask import render_template, redirect, url_for
from flask import request
import json
path=__file__[0:-9]
sys.path.insert(0,path)
import dispatcher

from main.sqla.app import create_app, get_user_for_prefix
#from main.web_apps_examples import *

from werkzeug.exceptions import NotFound


def make_app(prefix):
    print prefix
    user = get_user_for_prefix(prefix)
    if user is None:
       return NotFound()
    return create_app(user)

## from app.sqla import *
#from main.sqla.app import app as application
## application = app
#from main.web_apps_examples import *


