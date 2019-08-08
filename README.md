# fblktrace

The tool help report file system cache miss i/o block device using BPF tracing.  

1. Setup 

```sh
sudo bash -c "printf \"deb http://http.us.debian.org/debian unstable main non-free contrib\ndeb-src http://http.us.debian.org/debian unstable main non-free contrib\" >> /etc/apt/sources.list"
sudo apt update 
sudo apt install bpfcc-tools -y
wget https://raw.githubusercontent.com/rite2nikhil/fblktrace/master/fblktrace.py
wget https://raw.githubusercontent.com/rite2nikhil/fblktrace/master/report.py
```

2. Run FBLKTrace 

```sh
timeout -k 20 10 sudo python ./fblktrace.py 2>&1 /dev/null >> /tmp/bpf_out
```

3. Report

```sh
sudo python ./report.py /tmp/bpf_out
```

