import re                                                                                                                                                                                                          
import collections
import subprocess as sp

def run_gluster_command(cmd):
    """Execute gluster commands.

    args:
    cmd: String of command. ex. "gluster volume info <volname>""
    returns:
    tuple (ret,output,err)
    ret = return status of command
    output = output string
    err = error message if any
    """
    p = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
    (output, err) = p.communicate()
    ret = p.wait()
    return (ret, output, err)

def  get_device_file_dict():
    cmd = 'lshw -class disk'
    desc = "description"
    log_name = "logical name"
    serial = "serial"
    cdrom = "cdrom"

    dev = []
    dev_list = []

    ret, output, err = run_gluster_command(cmd)
    output = output.decode('ASCII')
    dev_info = output.split('\n')
    for line in dev_info:
        if re.search(desc, line):
            if dev:
                dev_list.append(dev)

            dev = []
        if re.search(log_name, line) or re.search(serial, line):
            temp = line.split(':')
            temp[1] = temp[1].strip(' ')
            dev.append(temp[1])
    dev_list.append(dev)
    for line in dev_list:
        print(line)

get_device_file_dict()
