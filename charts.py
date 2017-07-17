import os
import pymysql
from flask import Flask,render_template
import plotly.plotly as py
import plotly.graph_objs as go
    

app = Flask(__name__)
 # my sql
@app.route('/a')
def charts():
    MYSQL_DATABASE_HOST = os.getenv('IP','0.0.0.0')
    MYSQL_DATABASE_USER = 'satyasameer'
    MYSQL_DATABASE_PASSWORD = ''
    MYSQL_DATABASE_DB = 'my_flask_app'
    conn = pymysql.connect(
        host=MYSQL_DATABASE_HOST,
        user=MYSQL_DATABASE_USER,
        passwd=MYSQL_DATABASE_PASSWORD,
        db=MYSQL_DATABASE_DB
        )
    cursor = conn.cursor()
    cursor1 = conn.cursor()
    # execute SQL select statement
    cursor.execute("SELECT B FROM chart_data")
    cursor1.execute("SELECT A FROM chart_data")
    xvalues=[]
    yvalues=[]
    for i in cursor.fetchall():
        xvalues.append(i[0])
    
    for i in cursor1.fetchall():
        yvalues.append(i[0])
    
    
    print (xvalues);
    print (yvalues);
                    
    return render_template('chart3.html')
    
 
@app.route("/")
def chart():
    labels = ["January","February","March","April","May","June","July","August"]
    values = [10,9,8,7,6,4,7,8]
    colors = [ "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC"  ]
    return render_template('chart3.html', set=zip(values, labels, colors))
 
    
if __name__ == '__main__':
    host = os.getenv('IP','0.0.0.0')
    port = int(os.getenv('PORT',5000))
    app.debug = True
    app.secret_key = 'SuperSecretKey'
    app.run(host =host,port=port)
