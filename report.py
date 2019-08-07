#!/usr/bin/python    

import subprocess
import sys
import os

def getFileName(inum, dict): 
    if not inum in dict: 
        cmd = "find /var/lib/kubelet/pods/ -inum %s" % (inum)
        dict[inum]=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.read().rstrip()
    return dict[inum]
        
def split_list(n):
    """will return the list index"""
    return [(x+1) for x,y in zip(n, n[1:]) if y-x != 1]

def get_sub_list(my_list):
    """will split the list base on the index"""
    my_index = split_list(my_list)
    output = list()
    prev = 0
    for index in my_index:
        new_list = [ x for x in my_list[prev:] if x < index]
        output.append(new_list)
        prev += len(new_list)
    output.append([ x for x in my_list[prev:]])
    return output


def main():
   filepath = sys.argv[1]
   d = dict()
   b = dict()
   if not os.path.isfile(filepath):
       print("File path {} does not exist. Exiting...".format(filepath))
       sys.exit()
  
   with open(filepath) as fp:
       for line in fp:
           #print(line)
           args=line.strip().split('\t')
           if args.__len__() < 3:
               continue
           inum=args[1].split(":")[0]
           fileName=getFileName(inum, d)
           if fileName == '':
               continue
           #print(inum, d[inum])
           fsblk_parts=args[2].split("=")
           if fsblk_parts.__len__() != 2:
               continue
           fsblk = fsblk_parts[1]
           b.setdefault(inum, []).append(fsblk)
   for inum in d:
       file=d[inum]
       if file == '':
           continue
       print(os.path.relpath(file, "/var/lib/kubelet/pods/"), get_sub_list(b[inum]))

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

