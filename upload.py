from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/test'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))

    def __init__(self, username):
        self.username = username

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(64))

    def __init__(self, filename):
        self.filename = filename


class UserFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    fileid = db.Column(db.Integer)

    def __init__(self, userid, fileid):
        self.userid = userid
        self.fileid = fileid
@app.route('/')
def upload_file1():
    return render_template('upload.html')
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        #TODO: somehow get the current users id
        userid = request.form['userid'];

        f = request.files['file']
        targetDir = "uploads/"+str(userid)

        try:
            os.mkdir(targetDir)
        except:
            print("uploads already exists")
        f.save(targetDir+"/"+secure_filename(f.filename))

        #add the new file's name to database, TODO: change from name to directory
        newFile = File(f.filename)
        db.session.add(newFile)
        db.session.flush()  #flush so that newFile obj will get it's primary key

        fileid = newFile.id   #get id of the last insert


        userFile = UserFile(userid,fileid)
        db.session.add(userFile)

        db.session.commit()
        return str(userid)+'file uploaded successfully'


@app.route('/add_admin')
def add_admin():
    # assuming that username and fileid are sent through a GET request,
    # ex: http://localhost:5000/add_admin?username=myname&&fileid=69
    #

    currentUserId = 3  # idk how you're getting this, assume it's 1 for now
    username = request.args['username']  # username of the new user
    fileid = request.args['fileid']  # fileid of the file which new user is to be added to

    # verify if currentUserId belongs to file of fileid
    if UserFile.query.filter_by(userid=currentUserId, fileid=fileid).first() == None:
        return str(currentUserId) + " is not admin of " + str(fileid);

    # add current user to admins
    # TODO: need to check if username is aleardy an admin
    newUser = User.query.filter_by(username=username).first()
    newUserFile = UserFile(newUser.id, fileid)
    db.session.add(newUserFile)

    db.session.commit()
    return 'Successfully added new user_file (i.e. admin)'


if __name__ == '__main__':
    app.run(debug = True)
