#!/usr/bin/python
import sys
import os
from flask import Flask
from flask import render_template, redirect, url_for
from flask import request
import json

import logging
logging.basicConfig(stream=sys.stderr)
path=__file__[0:-10]
sys.path.insert(0,path)

from app import app as application
