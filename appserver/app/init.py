from flask import Flask,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user
from flask_mail import Mail,Message


app = Flask(__name__)
Bootstrap(app)
app.config.from_object('config')
db = SQLAlchemy(app)


##Init for Login
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

#For Mail
mail=Mail(app)


from app import views
