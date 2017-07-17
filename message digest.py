import sys
import time
import os
import hashlib



watchdir = '/home/mohith/Desktop/md'                     #entering into the path(Created a md folder at Desktop)
contents = os.listdir(watchdir)                          #assigning variable to the list of files in the md folder
count = len(watchdir)
dirmtime = os.stat(watchdir).st_mtime

counter = 0                                              #assigning global variabe 
otherfiles = []



while True:
    newmtime = os.stat(watchdir).st_mtime
    if newmtime != dirmtime:
        dirmtime = newmtime
        newcontents = os.listdir(watchdir)
        added = set(newcontents).difference(contents)          
        if added:                                                     #when a file enters into the folder
            print "Files added: %s" % (" ".join(added))





        removed = set(contents).difference(newcontents)            #when a file leaves the folder
        if removed:

            print "Files removed: %s" % (" ".join(removed))


#Finding the number of files in updated folder

        contents = newcontents
        for value in contents:
            print value
        for file in os.listdir(watchdir):
            try:
                otherfiles.append(file)
                counter = counter + 1
            except Exception as e:
                raise e
                print "No files found here!"
        print "Total files found:\t", counter
        counter = 0



        def hash_file(filename):
            """"This function returns the SHA-1 hash
            of the file passed into it"""

            # make a hash object
            h = hashlib.sha1()

            # open file for reading in binary mode
            with open(filename, 'rb') as file:
                # loop till the end of the file
                chunk = 0
                while chunk != b'':
                    # read only 1024 bytes at a time
                    chunk = file.read(1024)
                    h.update(chunk)

            # return the hex representation of digest
            return h.hexdigest()

#------------------------------------------------------------------------
#creating a new folder with all message digest values with file name and file directory.


        for (dirname, dirs, files) in os.walk('/home/mohith/Desktop/md'):
            for filename in files:
                thefile = os.path.join(dirname, filename)
                message = hash_file(thefile)
                print(message)
                os.chdir("/home/mohith/Desktop")
                msgdsg = open("message digest", 'a')
                msgdsg.write(thefile + '\n')
                msgdsg.write((message) + '\n')
                msgdsg.close()

#Refresh time for the folder.
    time.sleep(3)
