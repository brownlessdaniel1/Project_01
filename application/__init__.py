from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"]="mysql+pymysql://root:rooot@35.230.133.171/project_01"
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///test-db"
# app.config["SQLALCHEMY_DATABASE_URI"]=os.getenv("SQL_URI")
app.config["SECRET_KEY"]="SECRET_KEY"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False

db = SQLAlchemy(app)

from application import routes
