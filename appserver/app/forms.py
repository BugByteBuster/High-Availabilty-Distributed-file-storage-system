from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField
from flask_wtf.file import FileField,FileRequired
from wtforms.validators import InputRequired,DataRequired, Email, Length,IPAddress


#This class belong to the Login Page
class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired()])
    password = PasswordField('password', validators=[InputRequired()])
    remember = BooleanField('remember me')

#This class belong to the SignUp Page

class SignUp(FlaskForm):
    email=StringField('email',validators=[InputRequired(),Email(message='Invalid email'),Length(max=50)])
    username=StringField('username',validators=[InputRequired(),Length(min=4,max=15)])
    password=PasswordField('password',validators=[InputRequired(),Length(min=8,max=80)])

class FileUpload(FlaskForm):
    upload=FileField(validators=[FileRequired()])

class NewFolder(FlaskForm):
    foldername=StringField('foldername', validators=[InputRequired(),Length(min=4,max=15)])
