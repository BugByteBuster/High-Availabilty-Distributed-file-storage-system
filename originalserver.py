import os
import hashlib


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
for (dirname, dirs, files) in os.walk('/home/soumith/Desktop/retun'):
            for filename in files:
                thefile = os.path.join(dirname, filename)
                message = hash_file(thefile)
                print(message)
                os.chdir("/home/soumith/Desktop")
                msgdsg = open("returning_server", 'a')
                msgdsg.write(thefile + '\n')
                msgdsg.write((message) + '\n')
                msgdsg.close()
