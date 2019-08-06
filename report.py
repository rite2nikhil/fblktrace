#!/usr/bin/python    

import subprocess
import sys
import os

def getFileName(inum, dict): 
    if not inum in dict: 
        cmd = "find /Users/nikhil/ -inum %s" % (inum)
        dict[inum]=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.read().rstrip()
    return dict[inum]
        

def main():
   filepath = sys.argv[1]
   d = dict()
   b = dict()
   print(filepath)
   if not os.path.isfile(filepath):
       print("File path {} does not exist. Exiting...".format(filepath))
       sys.exit()
  
   with open(filepath) as fp:
       for line in fp:
           print(line)
           args=line.strip().split('\t')
           inum=args[1].split(":")[0]
           fileName=getFileName(inum, d)
           if fileName is '':
               continue
           fsblk=args[2].split("=")[1]
           b.setdefault(inum, []).append(fsblk)

   for key, val in d.items():
       if val is not '':
           print(val, b[key])
    
if __name__ == '__main__':
   main()


#cmd = "find /var/lib/kubelet/pods/ -inum $i | rev | cut -d'/' -f-3 | rev"
#i=3114014
#f=getFileName(i, d)
#print(f)
#f=getFileName(i, d)  
#print(f)
#returned_output=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.read()

# using decode() function to convert byte string to string
#print('File is:', d[i].decode("utf-8"))
