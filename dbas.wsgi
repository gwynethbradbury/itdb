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
from app.sqla.app import app as application
# application = app
