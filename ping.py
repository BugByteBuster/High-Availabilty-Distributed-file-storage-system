@app.route('/serverstatus',methods=['GET','POST'])
@login_required
def serstat():
    status1, result1 = sp.getstatusoutput("ping -c1 -w2 10.0.0.1")
    status2, result2 = sp.getstatusoutput("ping -c1 -w2 10.0.0.2")
    status3, result3 = sp.getstatusoutput("ping -c1 -w2 10.0.0.3")
    return render_template('server_status.html',stat1 = status1, stat2 = status2, stat3 = status3)

#scheduler = BackgroundScheduler()
#scheduler.start()
#scheduler.add_job(
#       func=serstat,
#       trigger=IntervalTrigger(seconds=6),
#       id='ping',
#       name='Serv_stat',
#       replace_existing=True)
#    # Shut down the scheduler when exiting the app
#atexit.register(lambda: scheduler.shutdown())
