#!/usr/bin/python
# @lint-avoid-python-3-compatibility-imports
#
# fblktrace.py  Trace page cache misses
#
# USAGE: fblktrace.py
#
# Copyright 2018 Collabora Ltd.
# Licensed under the Apache License, Version 2.0 (the "License")
#
# Author: Gabriel Krisman Bertazi  -  2018-09-20

from bcc import BPF

bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/fs.h>
#include <linux/kernel.h>

#define PAGE_SHIFT 12

#define fblktrace_container_of(ptr, type, member) ({			\
	const typeof(((type *)0)->member) * __mptr = (ptr);		\
	(type *)((char *)__mptr - offsetof(type, member)); })

int fblktrace_ext4_file_open(struct pt_regs *ctx, struct inode * inode,
				    struct file * filp)
{
	char lname[400];
	unsigned long ino = inode->i_ino;
	struct qstr qs = {};

	qs = filp->f_path.dentry->d_name;
	if (qs.len >= 400-1)
		qs.len = 399;

	bpf_probe_read(lname, 20, (void*)qs.name);

	bpf_trace_printk("Open inode %ld:fname = %s\\n", ino, lname);
	return 0;
}

// define output data structure in C
struct data_t {
    u32 pid;
    u64 ts;
	u32 inode;
	u32 fblk;
	u32 bsize;
	bool is_readahead;
    char comm[TASK_COMM_LEN];
};
BPF_PERF_OUTPUT(events);

int fblktrace_read_pages(struct pt_regs *ctx, struct address_space *mapping,
			 struct list_head *pages, struct page *page,
			 unsigned nr_pages, bool is_readahead)
{
	int i;
	u64 index;
	unsigned blkbits = mapping->host->i_blkbits;
	unsigned long ino = mapping->host->i_ino;;
 	u64 block_in_file;
	struct data_t data; 

	#pragma unroll
	for (i = 0; i < 32 && nr_pages--; i++) {
		if (pages) {
			pages = pages->prev;
			page = fblktrace_container_of(pages, struct page, lru);
		}
		index = page->index;
		block_in_file = (unsigned long) index << (12 - blkbits);
		
		data = {};
		data.pid = bpf_get_current_pid_tgid();
		data.ts = bpf_ktime_get_ns();
		data.inode=ino
		data.fsblk=index
		data.bsize=1<<blkbits
		data.isReadAhead = is_readahead
		
		bpf_get_current_comm(&data.comm, sizeof(data.comm));
		
		events.perf_submit(ctx, &data, sizeof(data));
	}
	return 0;
}

"""

#
#def getFileName(inum, dict): 
#    if not inum in dict: 
#        cmd = "find /var/lib/kubelet/pods/ -inum %s" % (inum)
#        dict[inum]=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.read().rstrip()
#    return dict[inum]
#

b = BPF(text=bpf_text)
b.attach_kprobe(event="ext4_mpage_readpages", fn_name="fblktrace_read_pages")
#b.attach_kretprobe(event="ext4_file_open",  fn_name="fblktrace_ext4_file_open");

# process event
start = 0
def print_event(cpu, data, size):
    global start
    event = b["events"].event(data)
    if start == 0:
            start = event.ts
    time_s = (float(event.ts - start)) / 1000000000
    print("%-18.9f %-16s %-6d %s" % (time_s, event.comm, event.pid,
        "Hello, perf_output!"))

# loop with callback to print_event
b["events"].open_perf_buffer(print_event)
while 1:
    b.perf_buffer_poll()
