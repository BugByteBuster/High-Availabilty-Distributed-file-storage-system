from flask_mail import Message
from app import app, url_for,mail

def send_email(to,subject,template):
    msg=Message(subject,recipients=[to],html=template,sender=app.config['MAIL_DEFAULT_SENDER'])
    mail.send(msg)
