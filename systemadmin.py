import os
import pymysql
from flask import Flask,request,render_template,redirect,url_for,flash,make_response,session,jsonify
app = Flask(__name__)



@app.route('/' , methods=['GET','POST'])
def sys():
    error = None
    number_of_servers=0;
    number_of_replicas=0;
    ip_list = [];
    if request.method == 'POST':
        number_of_servers = request.form.get('server')
        number_of_replicas = request.form.get('replica1')
        ip_list = request.form.getlist('dynamic[]')
        print(number_of_servers);
        print(number_of_replicas);
        print(ip_list);
    return render_template('System3.html' , error=error,server=number_of_servers,replicas = number_of_replicas)        
    
       
if __name__ == '__main__':
    host = os.getenv('IP','0.0.0.0')
    port = int(os.getenv('PORT',5001))
    app.debug = True
    app.secret_key = 'SuperSecretKey'
    app.run(host =host,port=port)
    
