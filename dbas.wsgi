#!/usr/bin/python
import sys
import os
from flask import Flask
from flask import render_template, redirect, url_for
from flask import request
import json
path=__file__[0:-9]
sys.path.insert(0,path)


# from app.sqla import *
from main.sqla.app import app as application
# application = app
from main.web_apps_examples import *
