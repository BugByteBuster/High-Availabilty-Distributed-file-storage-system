Python 3.6.1 (v3.6.1:69c0db5, Mar 21 2017, 17:54:52) [MSC v.1900 32 bit (Intel)] on win32
Type "copyright", "credits" or "license()" for more information.
>>> import smtplib
>>> fromaddr="visionquestbth@gmail.com"
>>> toaddr="nskk.505@gmail.com"
>>> message="this is python generated message"
>>> password="visionquest17"
>>> server=smtplib.SMTP('smtp.gmail.com:587')
>>> server.starttls()
(220, b'2.0.0 Ready to start TLS')
>>> server.login('visionquestbth@gmail.com','visionquest17')
(235, b'2.7.0 Accepted')
>>> server.sendmail('visionquestbth@gmail.com','nskk.505@gmail.com','this is python generated message')
{}
>>> server.quit()
(221, b'2.0.0 closing connection 22sm1898221ljv.67 - gsmtp')
>>> 
