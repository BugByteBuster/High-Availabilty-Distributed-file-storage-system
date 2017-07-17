import hashlib
import os
os.chdir(“/home/mohith/Documents”)
BLOCKSIZE = os.path.getsize(‘filename’)
hasher = hashlib.sha1()
with open(‘filename’, ‘rb’) as afile:
buf = afile.read(BLOCKSIZE)
while len(buf)>0:
hasher.update(buf)
buf = afile.read(BLOCKSIZE)
print hasher.hexdiest()


