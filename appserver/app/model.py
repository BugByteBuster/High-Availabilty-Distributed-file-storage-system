from app import db
from app import login_manager,UserMixin


class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50),unique=True)
    password = db.Column(db.String(80))
    confirm_pass=db.Column(db.Boolean)
    assets=db.relationship('Asset',backref='user',lazy='dynamic')
    shared=db.relationship('Shared',backref='user',lazy='dynamic')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Asset(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filename = db.Column(db.String(100))
    file_size=db.Column(db.Float(10,2))
    creation_date=db.Column(db.DateTime)
    modification_date=db.Column(db.DateTime)
    isitafolder=db.Column(db.Boolean,default=0)
    infolder=db.Column(db.String(15),default='none')
    route=db.Column(db.String(100),unique=True)
    isfileshared=db.Column(db.Boolean,default=0)
    messageDigest = db.Column(db.String(100)


class Shared(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    route=db.Column(db.String(100))
    isitafolder = db.Column(db.Boolean, default=0)
    owner=db.Column(db.String(50))
    sharedwith=db.Column(db.String(50),db.ForeignKey('user.username'))
    master=db.Column(db.Boolean,default=0)
    editor=db.Column(db.Boolean,default=0)
    reader=db.Column(db.Boolean,default=0)

