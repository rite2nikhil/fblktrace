#!/usr/bin/python    

import subprocess
import sys
import os
import os.path
from collections import namedtuple
EventData = namedtuple("EventData", "tid ts inode_num fs_blk blk_size is_readahead")

class EventData:
    def __init__(self, tid, ts, inode_num, fs_blk, blk_size, is_readahead):
        self.tid = tid
        self.inode_num=inode_num
        self.fs_blk=fs_blk
        self.blk_size=blk_size
        self.is_readahead=is_readahead 

def shorten_path(file_path, length):
    parts=file_path.split("/")
    return "/".join(parts[len(parts)-1-length:])

def getFileName(inum, dict): 
    if not inum in dict: 
        cmd = "find /var/lib/kubelet/pods/ -inum %s" % (inum)
        dict[inum]=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.read().rstrip()
    return dict[inum]
        
def split_list(n):
    """will return the list index"""
    return [(x+1) for x,y in zip(n, n[1:]) if y.fs_blk-x.fs_blk != 1]

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

def getRangeOutput(sub_lists):
    output = list()
    for sub_list in sub_lists:
        if sub_list.__len__() == 1:
            str = sub_list[0]
        else:
            str = "%d-%d" %(sub_list[0].fs_blk, sub_list[0].fs_blk+sub_list.__len__()-1) 
        output.append(str)
    return output

def main_old():
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
           fsblk_parts=args[2].split("=")
           if fsblk_parts.__len__() != 2:
               continue
           fsblk = int(fsblk_parts[1])
           b.setdefault(inum, []).append(fsblk)
   for inum in d:
       file=d[inum]
       if file == '':
           continue
       range_op=getRangeOutput(get_sub_list(b[inum]))
       print(shorten_path(file, 2), range_op)

#  ReplicaFetcherT-9311  [003] d... 91189.058312: : => inode: 135014595: FSBLK=35 BSIZ=4096 [RA]
def main():
    filepath = sys.argv[1]
    file_name_cache = dict()
    inode_events = dict()
    if not os.path.isfile(filepath):
       print("File path {} does not exist. Exiting...".format(filepath))
       sys.exit()
    with open(filepath) as fp:
       for line in fp:
           args=line.strip().split(" ")
           if args.__len__() < 10 or args.__len__() > 11 or line.find("FSBLK")==-1 :
               continue
           data=EventData(args[0], args[3], args[7].split(":")[0].strip(), args[8].split("=")[1].strip(), args[9].split("=")[1].strip(), False)
           if args.__len__() == 10:
               data.is_readahead= args[10]=="[RA]"
           inode_events.setdefault(data.inode_num, []).append(data)
    
    for inum in inode_events:
       fileName=getFileName(data.inode_num, file_name_cache)
       if fileName == '':
           continue
       range_op=getRangeOutput(get_sub_list(inode_events[inum]))
       print(shorten_path(fileName, 2), range_op)

if __name__ == '__main__':
    main()


