from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/PROJECT'
db = SQLAlchemy(app)


class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Servers = db.Column(db.String(64))
    status = db.Column(db.Boolean(),nullable=False, unique=True)
    
    def __init__(self, username):
        self.Servers = Servers
        self.status = status


if __name__ == '__main__':
    app.run(debug = True)
