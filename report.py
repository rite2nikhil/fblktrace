#!/usr/bin/python    

import subprocess
import sys
import os
import os.path

volume_search_path="/var/lib/kubelet/pods/"

class EventData:
    def __init__(self, tid, ts, inode_num, fs_blk, blk_size, is_readahead):
        self.tid = tid
        self.inode_num=inode_num
        self.fs_blk=fs_blk
        self.blk_size=blk_size
        self.is_readahead=is_readahead 

def shorten_path(file_path, length):
    if file_path == '':
        return ""
    parts=file_path.split("/")
    return "/".join(parts[len(parts)-1-length:])

def getFileName(inum, dict): 
    if not inum in dict: 
        cmd = "find %s -inum %s" % (volume_search_path, inum)
        file_name=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.read().rstrip()
        dict[inum]=shorten_path(str(file_name), 2)
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

def get_inum_output(events):
    tid_map = dict()
    for event in events:
        tid_map.setdefault(event.tid, []).append(event.fs_blk)
    output = list()
    for tid in tid_map:
        output.append("%s, %s"%(tid, get_range_output(get_sub_list(tid_map[tid]))))
    return output

def get_range_output(sub_lists):
    output = list()
    for sub_list in sub_lists:
        if sub_list.__len__() == 1:
            continue
        elif sub_list.__len__() == 1:
            str = "%d"%(sub_list[0])
        else:
            str="%d-%d"%(sub_list[0], sub_list[sub_list.__len__()-1])
        output.append(str)
    return output

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
           data=EventData(args[0], args[3], int(args[7].split(":")[0].strip()), int(args[8].split("=")[1].strip()), int(args[9].split("=")[1].strip()), False)
           if args.__len__() == 11:
               data.is_readahead= args[11]=="[RA]"
           inode_events.setdefault(data.inode_num, []).append(data)
    
    for inum in inode_events:
       fileName=getFileName(inum, file_name_cache)
       if fileName == '':
           continue
       print(fileName, get_inum_output(inode_events[inum]))

if __name__ == '__main__':
    main()


