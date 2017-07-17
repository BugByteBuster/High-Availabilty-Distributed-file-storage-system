import hashlib
import sys
import os
import time
def hash_file(filename):
    h = hashlib.sha1()
    with open(filename, 'rb') as file:
        chunk = 0
        while chunk != b'':
            chunk = file.read(1024)
            h.update(chunk)
    return h.hexdigest()
for (dirname, dirs, files) in os.walk('/home/soumith/Desktop/challenge'):
        for filename in files:
            thefile = os.path.join(dirname, filename)
            message = hash_file(thefile)
            print(message)
            os.chdir("/home/soumith/Desktop")
            msgdsg = open("messagedigest", 'a')
            #msgdsg.write(thefile + '\n')
            msgdsg.write((message) + '\n')
            msgdsg.close()
hosts0=open("/home/soumith/Desktop/messagedigest1")
hosts1=open("/home/soumith/Desktop/messagedigest2")
lines1=hosts0.readlines()
for i,lines2 in enumerate(hosts1):
    if lines2 != lines1[i]:
        print("Message Digest doesnot match")
    else:
        print("message digest match")

for(dirname, dirs, files) in os.walk('/home/soumith/Desktop'):
    for filename in files:
        thefile=os.path.join(dirname, filename)
        msgdsg=open("messagedigest",'w')
        msgdsg.close()          
