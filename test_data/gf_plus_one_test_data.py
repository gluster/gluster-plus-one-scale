"""Module to create test data like volume info and new bricks.

This module just provide functions to create file with volume
infomarion. Also, we can create a file with list of bricks of
new nodes.
"""


import collections
from scale.gf_logs import *
from scale.gf_plus_one_scale import *


def gf_test_get_new_bricks(new_node, total):
    bricks_list = []

    br = 1
    while br <= total:
        bricks_list.append(f'{new_node}:/root/brick-new-{br}')
        br += 1

    return bricks_list

def gf_get_test_volume_info(subvol=1, data=4, red=2):
    """Read the file containing volume info.

    Input: file name
    return: list of bricks
    """
    vol_config = collections.defaultdict(int)
    vol_info = collections.defaultdict()
    bricks_list = []
    total = subvol * (data + red)
    config = data + red
    host = 1
    br = 1
    sv = 0

    for i in range(1, total + 1):
        bricks_list.append(f'node-{host}:/root/brick-{sv}-{br}')
        if host == 3:
            host = 1
        else:
            host += 1

        if br == 6:
            br = 1
            sv += 1
        else:
            br += 1

    vol_config["brickCount"] = total
    vol_config["disperseCount"] = data + red
    vol_config["redundancyCount"] = red
    vol_config["subvolCount"] = subvol

    vol_info["bricks_list"] = bricks_list
    vol_info["vol_config"] = vol_config

    return vol_info


def create_gluster_v_info(subvol=1, data=4, red=2):
    """Create a file with volume info.

    Input:
    subvol = Number of subvolume
    data = number of data bricks
    red = redundancy

    Output: File gluster_v_info.txt with volume infomation
    """
    total = subvol * (data + red)
    config = data + red
    host = 1
    br = 1
    file_name = 'gluster_v_info.txt'
    file_out = open(file_name, 'w')

    vinfo = 'Volume Name: vol\n\
Type: Distributed-Disperse\n\
Volume ID: ea40eb13-d42c-431c-9c89-0153e834e67e\n\
Status: Started\n\
Snapshot Count: 0\n\
Number of Bricks: 6 x (4 + 2) = 36\n\
Transport-type: tcp\n\
Bricks:\n'
    sv = 0
    file_out.write(vinfo)
    for i in range(1, total + 1):
        file_out.write(f'Brick{i}: node-{host}:/root/brick-{sv}-{br}\n')
        if host == 3:
            host = 1
        else:
            host += 1

        if br == 6:
            br = 1
            sv += 1
        else:
            br += 1

    vinfo = 'Options Reconfigured:\n\
cluster.disperse-self-heal-daemon: disable\n\
transport.address-family: inet\n\
nfs.disable: on'
    file_out.write(vinfo)
    file_out.close()
    return file_name


def create_new_node_bricks(no_of_bricks=12, node_num=4, file_name='new-node.txt'):
    """Create file with new bricks.

    Input:  no_of_bricks - No of new bricks on new node
    node_num- Number of the node
    file_name - name of the file where we want to store this data

    return file_name
    """

    with open(file_name, 'w') as file_out:
        for i in range(1, no_of_bricks + 1):
            file_out.write(f'Brick{i}: node-{node_num}:/root/brick-{i}\n')

    return file_name


def gf_test_heal_info_when_glusterd_is_down():
    pass


def gf_test_vol_info_when_glusterd_is_down():
    pass


def gf_test_status_when_glusterd_is_down():
    pass


def gf_test_status_when_glusterd_is_down():
    pass

