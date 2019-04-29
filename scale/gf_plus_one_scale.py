"""This module provides common volume functions.

This module provide functions to create file with volume
information. Also, we can create a file with list of bricks of
new nodes.
"""


import re
import collections
import subprocess as sp
from scale.gf_exceptions import *
from scale.gf_logs import *
from test_data.gf_plus_one_test_data import *
import xml.etree.ElementTree as ET


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
    if ret:
        raise GfCommandFailed(f'ret = {ret}, out = {output.decode("ascii")}, error = {err.decode("ascii")}')

    return (ret, output, err)


def gf_get_new_bricks_list(filename):
    """Get list of bricks from file provided.

    Input: File Name which contains list of bricks
    return: Brick list in the form of "LIST"
    """
    bricks_list = []
    try:
        with open(filename, 'r') as file_out:
            bricks_list = file_out.readlines()
            for i in range(0, len(bricks_list)):
                bricks_list[i] = bricks_list[i].rstrip()

    except FileNotFoundError as er:
        glogger.error(er)
        raise GfCommandFailed(er)
    else:
        return bricks_list


def gf_get_volume_info_xml(volname):
    """Get volume heal summary using gluster command.

    Input: volume name
    return: Complete volume info in a dict of
    bricks_list and vol_config
    """
    vol_config = collections.defaultdict(int)
    bricks_list = []

    vol_info = collections.defaultdict()

    cmd = 'gluster v info ' + volname + ' --xml'
    ret, output, err = run_gluster_command(cmd)
    root = ET.fromstring(output)

    for brick in root.iter('brick'):
        for name in brick.findall('name'):
            brick_name = name.text
            bricks_list.append(brick_name)

    for count in root.iter('brickCount'):
        vol_config["brickCount"] = int(count.text)

    for count in root.iter('disperseCount'):
        vol_config["disperseCount"] = int(count.text)

    for count in root.iter('redundancyCount'):
        vol_config["redundancyCount"] = int(count.text)

    vol_config["subvolCount"] = int(vol_config["brickCount"] / vol_config["disperseCount"])

    vol_info["bricks_list"] = bricks_list
    vol_info["vol_config"] = vol_config
    glogger.info(vol_info)

    return vol_info


def gf_get_volume_heal_summary_xml(volname):
    """Get volume heal summary using gluster command.

    Input: volume name
    return: Complete volume heal summary in a dictionary
    'brick_path' : status
    """
    status = 0
    heal_status_dict = collections.defaultdict(int)
    cmd = 'gluster v heal ' + volname + ' info summary --xml '
    ret, output, err = run_gluster_command(cmd)
    root = ET.fromstring(output)

    for brick in root.iter('brick'):
        for name in brick.findall('name'):
            brick_name = name.text

        for entries in brick.findall('totalNumberOfEntries'):
            status = int(entries.text)

        heal_status_dict[brick_name] = status

    glogger.debug(heal_status_dict)
    return heal_status_dict


def gf_get_volume_status_xml(volname):
    """Get volume status using gluster command.

    Input: volume name
    return:
    volume_status : Complete volume status in a dictionary
    'brick_path' : status
    """
    brick_status_dict = collections.defaultdict(int)

    cmd = 'gluster v status --xml ' + volname
    ret, output, err = run_gluster_command(cmd)
    root = ET.fromstring(output)

    for node in root.iter('node'):
        for path in node.findall('path'):
            brick = path.text

        for status in node.findall('status'):
            status = int(status.text)

        if re.search(brick, 'localhost'):
            continue

        brick_status_dict[brick] = status

    glogger.info(brick_status_dict)
    return brick_status_dict


def gf_get_volume_config(volume_info):
    """Fetch configuration od EC volume from volume info.

    Input: volume_info in the for of list
    return: Dictionary of volume config
    containing:
    {'data': <Number of data bricks>,
    'redundancy': <Number of redundance bricks>,
    'bricks': <Total number of bricks>,
    'subvols': <Number of subvolumes>}
    """
    volume_config = volume_info["vol_config"]
    glogger.info(volume_config)
    return volume_config


def gf_get_volume_bricks_list(volume_info):
    """Fetch bricks from volume info.

    Input:
    volume_info - in the form of list
    return: list of bricks in the form of
    hostname:<mount-path>
    """
    all_brick_list = volume_info["bricks_list"]
    glogger.info(all_brick_list)
    return all_brick_list


def gf_get_node_to_bricks_dict(all_brick_list):
    """Get bricks of individual hosts.

    Input:
    all_brick_list - list of all the bricks per host
    return: dict in the form of
    'hostname':[brick1, brick2] containing all the host - bricks
    """
    all_brick_dict = collections.defaultdict(list)

    for line in all_brick_list:
        host_brick = line.split(':', 1)
        all_brick_dict[host_brick[0]].append(host_brick[1])

    glogger.info(all_brick_dict)
    return all_brick_dict


def gf_subvol_host_to_bricks_dict(brick_list, brcount):
    """List of subvolumes and its corresponding bricks.

    Input:
    brick_list - list of bricks of volume
    brcount : brick count for one subvolume (data + redundancy)

    return: list of dicts in the form of
    'hostname':[brick1, brick2] for individual subvolumes
    """
    subvol_brick_list = []
    host_brick = collections.defaultdict(list)
    i = 0

    for br in brick_list:
        brick = br.split(':', 1)
        host_brick[brick[0]].append(brick[1])
        i += 1
        if (i == brcount):
            subvol_brick_list.append(host_brick)
            host_brick = collections.defaultdict(list)
            i = 0

    glogger.info(f'************List of subvolumes and its corresponding bricks************')
    glogger.info(subvol_brick_list)
    return subvol_brick_list


def gf_subvol_bricks_list(volume_info):
    """List of subvolumes and its corresponding bricks.

    Input: volume_info in the form of list
    return: list of bricks in the form of
    'hostname':<mount-path>
    The length of this list will be equal to the
    number of subvolume in this volume
    """
    brick_list = gf_get_volume_bricks_list(volume_info)
    vlconfig = gf_get_volume_config(volume_info)
    brcount = vlconfig['disperseCount']
    glogger.info(f'Bricks per EC subvolume = {brcount}')
    return gf_subvol_host_to_bricks_dict(brick_list, brcount)
