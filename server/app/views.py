from flask import request,jsonify,abort
from app import app
import base64,os,json,shutil

#myIPBroadcaster
@app.route('/api/v1.0/ip_upload',methods=['POST'])
def ip_upload():
    data=[]
    json_dict=request.get_json()
    myPath="/tmp/visionquest/conf/"
    if not os.path.exists(myPath):
        os.makedirs(myPath)
    with open(myPath+'/'+'IPconfig.txt','a')as f:
        json.dump(json_dict,f)
    for i in range(0,len(json_dict)):
        servername=json_dict[i]['servername']
        ipaddr=json_dict[i]['ipaddr']
        data.append({'servername':servername,'ipaddr':ipaddr})
    return jsonify(data),201


#myUpload files API
@app.route('/api/v1.0/upload',methods=['POST'])
def tester():
    if not request.json or not 'filename' in request.json:
        abort(400)
    json_dict = request.get_json()
    filename=json_dict['filename']
    file= json_dict['file']
    username=json_dict['username']
    route=json_dict['route']
    root="/home/jamch/Documents/rootdata/"
    location=root+username
    if not os.path.exists(location):
        os.makedirs(location)
    f1=file.encode()
    f2=base64.b64decode(f1)
    newfile=root+route
    if os.path.exists(newfile):
        abort(409)  # Conflict because the File exist
    with open(newfile,'wb') as yepa:
        yepa.write(f2)
    data={'filename':filename,'username':username}
    return jsonify(data),201

#myModify file API
@app.route('/api/v1.0/modifyfile',methods=['PUT'])
def modifyfile():
    if not request.json or not 'filename' in request.json:
        abort(400)
    json_dict = request.get_json()
    filename=json_dict['filename']
    file= json_dict['file']
    username=json_dict['username']
    route=json_dict['route']
    root="/home/jamch/Documents/rootdata/"
    location=root+route
    if not os.path.exists(location):
        abort(409) # Conflict because the file doesnt exist
    f1=file.encode()
    f2=base64.b64decode(f1)
    with open(location,'wb') as f:
        f.write(f2)
    data={'filename':filename,'username':username}
    return jsonify(data),200













#myFolderCreated
@app.route('/api/v1.0/newfolder',methods=['POST'])
def newfolder():
    json_dict=request.get_json()
    foldername=json_dict['foldername']
    username = json_dict['username']
    root = "/home/jamch/Documents/rootdata/"
    location=root+username+"/"+foldername
    if os.path.exists(location):
        abort(409) # Conflict because the folder exist already
    else:
        os.makedirs(location)
    data={'foldername':foldername,'username':username}
    return jsonify(data),201

#myFolderDelete
@app.route('/api/v1.0/deletefolder/<path:route>',methods=['DELETE'])
def apiDeleteFolder(route):
    root="/home/jamch/Documents/rootdata/"
    myPath = root + route
    if not os.path.exists(myPath):
        abort(404)
    shutil.rmtree(myPath)
    data={'route':route}
    return jsonify(data),200 #200 or 204 positive


#myDownload API
@app.route('/api/v1.0/download/<path:route>')
def apiDownload(route):
    root = "/home/jamch/Documents/rootdata/"
    var=route.split('/')
    if len(var)==1:
       abort(400)  #Bad Request
    myPath=root+route
    if not os.path.exists(myPath):
        abort(404)
    with open(myPath,'rb') as f:
        filecontents=f.read()
    dataEncoded=base64.b64encode(filecontents)
    dataDecoded=dataEncoded.decode()
    data={'filename':var[-1],'file':dataDecoded}
    return jsonify(data),200

#myDownload API for folders
@app.route('/api/v1.0/downloadfolder/<path:route>') #The route consists of username/foldername
def downloadFolder(route):
    root = "/home/jamch/Documents/rootdata/"
    var=route.split('/')
    if len(var)==1:
       abort(400)  #Bad Request a folder was not specified
    myPath=root+route
    if not os.path.exists(myPath):
        abort(404)
    #We need to get all files inside a folder
    data=list()
    filesInFolder=os.listdir(myPath)
    for item in filesInFolder:
        with open(myPath+"/"+item,'rb') as f:
            filecontents=f.read()
        dataEncoded=base64.b64encode(filecontents)
        dataDecoded=dataEncoded.decode()
        data.append({'filename':item,'file':dataDecoded})
    return jsonify(data),200




#myDelete API
@app.route('/api/v1.0/delete/<path:route>',methods=['DELETE'])
def apiDelete(route):
    root="/home/jamch/Documents/rootdata/"
    myPath = root +route
    os.remove(myPath)
    data={'route':route}
    return jsonify(data),200 #200 or 204 positive

