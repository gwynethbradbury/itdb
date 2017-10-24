# from danceapp.database.seed import run_seed
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import main.iaas.iaas as iaas
import dbconfig








# if __name__ == '__main__':
iaas.db.create_all()

# SQL:
# create database taskmanagement;

# Python:
# python setup_db.py

# SQL:
# use taskmanagement
# insert into tag (name,color) values ('DBAS',3);
# insert into tag (name,color) values ('Online Learning',2);