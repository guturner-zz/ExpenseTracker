import os
import sys
from flask import Flask
from flask.ext.moment import Moment
from models import db

app = Flask(__name__)
app.config.from_object("config")
moment = Moment(app)

#mode is either dev or empty
try:
    mode = sys.argv[1]
except:
    mode = None
if mode == "dev":
    #makes the host the localhost when run with "dev"
    app.config["HOST"] = app.config["LOCALHOST"]

app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://' + app.config["USERNAME"] + ':' +\
                          app.config["PASSWORD"] + '@' + app.config["HOST"] + ':3306/' + app.config["DB_NAME"]

# Setup SQLAlchemy:
db.init_app(app)

import views