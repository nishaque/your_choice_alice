from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./content/data.db?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()
from models import db
db.init_app(app)
import views



# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app







