from flask import render_template,flash, redirect,url_for,request,jsonify,abort,send_from_directory,after_this_request
from app import app,db,login_required,login_user,current_user,logout_user
from .forms import LoginForm,SignUp,FileUpload,NewFolder
from .model import *
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from .token import generate_token,confirm_token,SignatureExpired
from .email import send_email
from sqlalchemy import exc
import base64,requests,os,shutil
from datetime import datetime
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import subprocess as sp
import time

@app.route('/')
@app.route('/index')
def index():
    return render_template("home.html")

@app.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()

    if form.validate_on_submit():
        user=User.query.filter(User.username==form.username.data).first()
        if user:
            if check_password_hash(user.password,form.password.data):
                if user.confirm_pass:
                    login_user(user,remember=form.remember.data)
                    return redirect(url_for('dashboard'))
                else:
                    flash("You need to confirm the link in the email")
                    return redirect(url_for('login'))
                    #return "You need to confirm the link in the email"
        flash('Invalid User')
        return redirect(url_for('login'))
    return render_template('login.html',form=form)

@app.route('/signup',methods=['GET','POST'])
def signup():
    form=SignUp()
    if form.validate_on_submit():
        try:
            hashed_password=generate_password_hash(form.password.data,method='sha256')
            new_user=User(username=form.username.data,email=form.email.data,password=hashed_password,confirm_pass=False)
            db.session.add(new_user)
            db.session.commit()

            email = form.email.data
            token = generate_token(email)
            confirm_url = url_for('confirm_email', token=token, _external=True)
            html = render_template('Message.html', confirm_url=confirm_url)
            subject = "Please confirm your email"
            send_email(email, subject, html)

            return 'Your User has been created please check your email!!'
        except exc.IntegrityError:
            flash('The user or email already exist in the system')
            #return "<h1>The user or email already exist in the!!</h1>"
            return redirect(url_for('signup'))

    return render_template('signup.html',form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    user=User.query.filter(User.username==current_user.username).first()
    #otherusers=User.query.filter(User.username!=current_user.username).all()
    identity=user.id
    element=Asset.query.filter(Asset.user_id==identity,Asset.infolder=='none').order_by(Asset.isitafolder).all()
    return render_template("dash.html",name=current_user.username,element=element)#,otherusers=otherusers)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email=confirm_token(token)
        user=User.query.filter(User.email==email).first()
        user.confirm_pass=True
        db.session.commit()
    except SignatureExpired:
        flash('The confirmation link is invalid or has expired. You need to register again')
        return redirect(url_for('signup'))
    flash('Congrats your account has been validated!!!')
    return redirect(url_for('login'))


#FrontEnd Upload Interface
@app.route('/upload/<path:route>',methods=['GET','POST'])
@login_required
def upload(route):
    file = request.files[route]
    filename=secure_filename(file.filename)
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename)) # We save the file into the local repo
    #We proceed to send the file to the remote server
    #1 Prepare the object to be sent
    myPath=os.path.join(app.config['UPLOAD_FOLDER'],filename)
    with open(myPath,'rb') as f:
        filecontent=f.read()
    dataEncoded = base64.b64encode(filecontent)
    dataDecoded = dataEncoded.decode()
    data = {'username': current_user.username, 'filename': filename, 'file': dataDecoded,'route':route+'/'+filename}
    myurl='http://localhost:4001/api/v1.0/upload'
    r=requests.post(myurl,json=data)
    var = route.split('/')
    @after_this_request
    def remove_file(response):
        os.remove(myPath)
        return response
    if r.status_code==201:
        #Getting the size of the file:
        file_size=os.path.getsize(myPath) #in bytes
        # message digest
            hasher = hashlib.sha1()
            #print(file_size)
            with open(myPath, 'rb') as afile:
                buf = afile.read(file_size)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = afile.read(file_size)
            message_digest=hasher.hexdigest()
            #print(message_digest)
        
        #Checking
        # Writing information to db
        user_object=User.query.filter(User.username==current_user.username).first()
        if len(var)==1:
            newAsset=Asset(user_id=user_object.id,filename=filename,file_size=file_size,creation_date=datetime.now(),
                       modification_date=datetime.now(),route=route+"/"+filename,messageDigest=message_digest)#,isitafolder=0)
            db.session.add(newAsset)
        else:
            newAsset=Asset(user_id=user_object.id,filename=filename,file_size=file_size,creation_date=datetime.now(),
                         modification_date=datetime.now(),infolder=var[1],route=route+"/"+filename)#,)
            db.session.add(newAsset)
        db.session.commit()
        flash('The file has been successfully uploaded!!')
    elif r.status_code==409:
        if len(var)==1:
            flash("There is a file with the same name")
        else:
            flash("There is a file with the same name in the folder [{}]".format(var[1]))
    else:
        flash('Error: The file was not uploaded!!')
    return redirect(url_for('dashboard'))


#FrontEnd Download Interface
@app.route('/download/<path:route>',methods=['GET','POST'])
@login_required
def download(route):
    myUrl='http://localhost:4001/api/v1.0/download/'+route
    r=requests.get(myUrl)
    if r.status_code==200:
        json_dict =r.json()
        filename=json_dict['filename']
        username=current_user.username
        file= json_dict['file']
        dataEncoded=file.encode()
        dataDecoded=base64.b64decode(dataEncoded)
        myPath=os.path.join(app.config['DOWNLOAD_FOLDER'],username)
        if not os.path.exists(myPath):
            os.makedirs(myPath)
        with open(myPath+"/"+filename,'wb') as f:
            f.write(dataDecoded)
        @after_this_request
        def remove_file(response):
            shutil.rmtree(myPath) #Remove an entire folder
            return response
        return send_from_directory(myPath,filename,as_attachment=True)

# FrontEnd Download Interface folder
@app.route('/downloadfolder/<path:route>', methods=['GET', 'POST'])
@login_required
def downloadfolder(route):
    var=route.split('/')
    myUrl='http://localhost:4001/api/v1.0/downloadfolder/'+route #username+foldername
    r=requests.get(myUrl)
    if r.status_code==200:
        myPath = os.path.join(app.config['DOWNLOAD_FOLDER']+current_user.username+'/',var[-1])
        if not os.path.exists(myPath):
            os.makedirs(myPath)
        json_dict =r.json()
        if not json_dict:
            flash('The folder [{}] you want to download is empty!!'.format(var[-1]))
            return redirect(url_for('dashboard'))
        for i in range(0,len(json_dict)):
            filename=json_dict[i]['filename']
            file= json_dict[i]['file']
            dataEncoded=file.encode()
            dataDecoded=base64.b64decode(dataEncoded)
            with open(myPath+"/"+filename,'wb') as f:
                f.write(dataDecoded)
        #We prepare to zip the folder
        ziparchivepath=shutil.make_archive(myPath,'zip',myPath)
        hp=ziparchivepath.split('/')
        @after_this_request
        def remove_file(response):
            shutil.rmtree(app.config['DOWNLOAD_FOLDER']+current_user.username) #Remove an entire folder
            return response
        return send_from_directory(app.config['DOWNLOAD_FOLDER']+current_user.username,hp[-1], as_attachment=True)


#frontEnd Delete Files Interface
@app.route('/delete/<path:route>',methods=['DELETE','GET'])
@login_required
def delete(route):
    myUrl = 'http://localhost:4001/api/v1.0/delete/' + route
    r=requests.delete(myUrl)
    if r.status_code==200:
        #We remove the dependecies of the file:
        removefileshared=Shared.query.filter(Shared.route==route).all()
        #We determine the foldername the file is, and if the folder is empty we remove the name from the shared table
        fileelement=Asset.query.filter(Asset.route==route).first()
        if removefileshared:
            for item in removefileshared:
                db.session.delete(item)
        #If the folder is empty we remove it:
        if fileelement.infolder!='none':
            routeobjectfolder=Asset.query.filter(Asset.filename==fileelement.infolder).first()
            fileobjinfolder=Shared.query.filter(Shared.route.like(routeobjectfolder.route+'/'+"%")).first()
            if not fileobjinfolder:
                folderobjectroute=Shared.query.filter(Shared.route==routeobjectfolder.route).first()
                db.session.delete(folderobjectroute)
        #Proceed to Delete information from data base
        file=Asset.query.filter(Asset.route==route).first()
        db.session.delete(file)
        db.session.commit()
    return redirect(url_for('dashboard'))

#FrontEnd Delete Folder Interface
@app.route('/deletefolder/<path:route>',methods=['DELETE','GET'])
@login_required
def deletefolder(route):
    myUrl='http://localhost:4001/api/v1.0/deletefolder/'+route
    r=requests.delete(myUrl)
    if r.status_code==200:
        #file = Asset.query.filter(db.or_(Asset.route == foldername ,Asset.infolder==foldername)).all()
        file = Asset.query.filter(Asset.route.like(route+"%")).all()
        fileshared=Shared.query.filter(Shared.route.like(route + "%")).all()
        #We delete the dependencies:
        for item in file:
            db.session.delete(item)
        for item1 in fileshared:
            db.session.delete(item1)
        db.session.commit()
    else:
        flash('The folder was not found')
    return redirect(url_for('dashboard'))

#Interface for the Share botton in the folder(Delete)
@app.route('/deletefoldersharing/<grant_user>/<path:route>')
@login_required
def deletefoldersharing(grant_user,route):
    fileobjinfolder = Shared.query.filter(Shared.route.like(route + "%"),Shared.sharedwith==grant_user).all()
    if fileobjinfolder:
        for el in fileobjinfolder:
            db.session.delete(el)
        db.session.commit()
    flash('The roles over the folder were removed!!')
    return redirect(url_for('dashboard'))

#Interface for the Share botton in the folder(update)
@app.route('/updatefoldersharing/<grant_user>/<path:route>',methods=['GET','POST'])
@login_required
def updatefoldersharing(grant_user,route):
    if grant_user not in request.form:
        flash('You did not update the role,please select one choice and do it again')
        return redirect(url_for('dashboard'))
    option=request.form[grant_user]
    fileobjinfolder = Shared.query.filter(Shared.route.like(route + "%"),Shared.sharedwith==grant_user).all()#).all()#,
    if option == 'master':
        for item in fileobjinfolder:
            item.master=1
            item.editor=0
            item.reader=0
    elif option == 'reader':
        for item in fileobjinfolder:
            item.master=0
            item.editor=0
            item.reader=1
    else:
        for item in fileobjinfolder:
            item.master=0
            item.editor=1
            item.reader=0
    db.session.commit()
    flash('The role for the folder to {} was updated'.format(grant_user))
    return redirect(url_for('dashboard'))


#Modify
@app.route('/modify/<path:route>',methods=['GET','POST','PUT'])#route=user/filename
@login_required
def modify(route):
    #Do some checking
    var=route.split('/')
    file_name=var[-1]
    file=request.files[route]
    filename = secure_filename(file.filename)
    if filename!=file_name:
        flash('The file uploaded differs from {}'.format(file_name))
        return redirect(url_for('dashboard'))
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # We save the file into the local repo
        # We proceed to send the file to the remote server
        # 1 Prepare the object to be sent
    myPath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(myPath, 'rb') as f:
        filecontent = f.read()
    dataEncoded = base64.b64encode(filecontent)
    dataDecoded = dataEncoded.decode()
    data = {'username': current_user.username, 'filename': filename, 'file': dataDecoded,'route':route}
    myurl = 'http://localhost:4001/api/v1.0/modifyfile'
    r = requests.put(myurl, json=data)
    print("DEBUG {}".format(r.status_code))
    @after_this_request
    def remove_file(response):
        os.remove(myPath)
        return response
    if r.status_code == 200:
        # Writing information to db
        user_object = Asset.query.filter(Asset.filename==filename).first()
        user_object.modification_date=datetime.now()
        db.session.commit()
        flash('The file has been successfully updated!!')
        return redirect(url_for('dashboard'))
    else:
        flash("There was a error in updating")
        return redirect(url_for('dashboard'))


#This is in case of share files and folders
@app.route('/share/<path:route>',methods=['GET','POST'])
@login_required
def share(route):
    var=route.split('/')
    #We determine the owner of the file:
    #element = User.query.filter(User.username != current_user.username,User.confirm_pass==1,User.username!=).all()
    element = User.query.filter(User.username != var[0],User.username != current_user.username,User.confirm_pass == 1).all()
    sharedusers=[r.sharedwith for r in Shared.query.filter(Shared.route==route)]
    return render_template("share.html",route=route,filename=var[-1],name=current_user.username,
                           sharedusers=sharedusers,element=element)


#Share files only
@app.route('/sharegrant/<grant_user>/<path:route>',methods=['GET','POST'])
@login_required
def grant(route,grant_user):
    if grant_user not in request.form:
        flash('You did not grant any roll,please do it again')
        return redirect(url_for('dashboard'))
    option=request.form[grant_user]
    #We determine if the item is a file or folder:
    itemobject=Asset.query.filter(Asset.route==route).first()
    isafolder=itemobject.isitafolder
    #We write in the DB
    if not isafolder:
        if option=='master':
            element=Shared(route=route,owner=current_user.username,sharedwith=grant_user,master=1)
            db.session.add(element)
        elif option=='reader':
            element = Shared(route=route,owner=current_user.username, sharedwith=grant_user, reader=1)
            db.session.add(element)
        else :
            element = Shared(route=route,owner=current_user.username, sharedwith=grant_user, editor=1)
            db.session.add(element)
    else:
        #We shared the entire folder
        foldername=itemobject.filename
        filesinfolder=Asset.query.filter(Asset.infolder==foldername).all()
        if not filesinfolder:
            flash('No files to share, The folder is empty!!')
            return redirect(url_for('dashboard'))
        #CHECK: If there is a file from the folder shared already, we remove it:
        routesinthefolder=[r.route for r in filesinfolder]
        for rev in routesinthefolder:
            filetoremove=Shared.query.filter(Shared.route==rev,Shared.sharedwith==grant_user).first()
            if filetoremove:
                db.session.delete(filetoremove)
        if option=='master':
            folderelement=Shared(route=route,isitafolder=1,owner=current_user.username,sharedwith=grant_user,master=1)
            db.session.add(folderelement)
            for n in filesinfolder:
                element=Shared(route=n.route,owner=current_user.username,sharedwith=grant_user,master=1)
                db.session.add(element)
        elif option=='reader':
            folderelement=Shared(route=route,isitafolder=1,owner=current_user.username,sharedwith=grant_user,reader=1)
            db.session.add(folderelement)
            for n in filesinfolder:
                element=Shared(route=n.route,owner=current_user.username,sharedwith=grant_user,reader=1)
                db.session.add(element)
        else :
            folderelement=Shared(route=route,isitafolder=1,owner=current_user.username,sharedwith=grant_user,editor=1)
            db.session.add(folderelement)
            for n in filesinfolder:
                element=Shared(route=n.route,owner=current_user.username,sharedwith=grant_user,editor=1)
                db.session.add(element)

    original=Asset.query.filter(Asset.route==route).first()
    original.isfileshared=1
    db.session.commit()
    flash("You have given {} permission as {} over {}".format(grant_user,option,itemobject.filename))
    return redirect(url_for('dashboard'))


@app.route('/newfolder',methods=['GET','POST'])
@login_required
def newfolder():
    form=NewFolder()
    if form.validate_on_submit():
        foldername=form.foldername.data
        url='http://localhost:4001/api/v1.0/newfolder'
        r=requests.post(url,json={'foldername':foldername,'username':current_user.username})
        if r.status_code==201:
            user_object = User.query.filter(User.username == current_user.username).first()
            newAsset = Asset(user_id=user_object.id, filename=foldername, file_size=0,
                             creation_date=datetime.now(), modification_date=datetime.now(),isitafolder=1,route=current_user.username+'/'+foldername)
            db.session.add(newAsset)
            db.session.commit()
            flash("The Folder [{}] was successfully created".format(foldername))
            return redirect(url_for('dashboard'))
        else:
            flash("A folder with name {} already exist".format(foldername))
            return redirect(url_for('dashboard'))
    return render_template('newfolder.html',form=form)


#Infolder Interface
@app.route('/infolder/<foldername>')
@login_required
def infolder(foldername):
    #Here query
    user_object = User.query.filter(User.username == current_user.username).first()
    element=Asset.query.filter(Asset.user_id==user_object.id,Asset.infolder==foldername).order_by(Asset.creation_date).all()
    return render_template('insidefolder.html',name=current_user.username,foldername=foldername,element=element)


#Route to MyShareFile option Dashboard
@app.route('/sharedfiles')
@login_required
def sharedfiles():
    #We query the files that has been shared with me
    element=Shared.query.filter(Shared.sharedwith==current_user.username).all()
    return render_template('sharedfiles.html',element=element)


#Route to My Audit
@app.route('/myaudit')
@login_required
def myaudit():
    #We query the files the user has shared to others
    element=Shared.query.filter(Shared.owner==current_user.username,Shared.isitafolder==0).all()
    return render_template('myaudit.html',element=element)


#def ipcheck():
 #   stat = []
 #   for p in range(1, 4):
 #       pop = "10.0.0." + str(p)
 #       status,result= sp.getstatusoutput("ping -c1 " + str(pop))
 #       stat = status
 #       if status == 0:
 #           print("System " + str(pop) + " is UP !")
 #       else:
 #           print("System " + str(pop) + " is DOWN !")




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

#Route to Plot Series
@app.route('/plotseries')
@login_required
def plotseries():
    labels = ["server1", "server2", "server3"]

    serv1_size = 0
    serv2_size = 0
    serv3_size = 0
 
    #to query file size from db
    user = User.query.filter(User.username == current_user.username).first()
    # otherusers=User.query.filter(User.username!=current_user.username).all()
    identity = user.id
    element = Asset.query.filter(Asset.user_id == identity).all()
    #colors = [ "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC"  ]
    #for i in element:
    #    print(i.file_size)

    for i in element:
    #    print(serv1_size)
        serv1_size =serv1_size + (i.file_size/1000)

    values = [serv1_size,serv2_size,serv3_size]

    return render_template('plotseries.html',values=values,labels=labels)


##System Administration GUI
@app.route('/sysadmin' , methods=['GET','POST'])
@login_required
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
    return render_template('SystemAdmin.html' , error=error,server=number_of_servers,replicas = number_of_replicas)
