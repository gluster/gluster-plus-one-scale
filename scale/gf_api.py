"""This module provides API's to scale EC volume."""


import collections
import scale.gf_plus_one_scale as sc
import test_data.gf_plus_one_test_data as test
from scale.gf_logs import glogger
from scale.gf_exceptions import (VolumeNotHealthy,
                                 GfCommandFailed)


def gluster_check_bricks_status(vol_name):
    """Check gluster volume status.

    Input:
    vol_name - Name of the volume.
    return :
    True - If all the bricks are UP
    False - If even a single brick of the volume is not UP
    """
    ret = True
    bricks_status = sc.gf_get_volume_status_xml(vol_name)
    for brick, status in bricks_status.items():
        if not status:
            glogger.error(f'Brick Down: {brick}, {status}')
            ret = False

    return ret


def gluster_check_volume_heal_summary(vol_name):
    """Check if a gluster volume needs heal.

    Input:
    vol_name - Name of the volume.
    return :
    True - Volume is healthy, No heal required.
    False - Volume is not healthy, heal required.
    """
    ret = True
    heal_summary = sc.gf_get_volume_heal_summary_xml(vol_name)
    if not heal_summary:
        return False

    for brick, status in heal_summary.items():
        if status:
            glogger.info(f'Need Heal: {brick}, {status}')
            ret = False

    return ret


def gluster_check_volume_health(vol_name):
    """Check if volume is healthy or not.

    Input :
    vol_name - Name of the volume.
    return :
    True - If volume is healthy. All the bricks are UP and nothing
    to heal for the volume.
    False - If volume is not healthy.
    """
    if not gluster_check_volume_heal_summary(vol_name):
        glogger.info("{vol_name} is not healthy ")
        return False

    if not gluster_check_bricks_status(vol_name):
        glogger.info("All the bricks of, {vol_name}, are not UP ")
        return False

    glogger.info("{vol_name}, is healthy, all the bricks are UP ")
    return True


def gf_are_bricks_sufficient(vol_config, list_of_empty_drives):
    """Check if the given bricks are sufficient for scaling."""
    """
    Input : volume config as dictionary
    list of empty drives
    return True - can be scaled
    False - Can not scale
    """
    disperse_count = vol_config['disperseCount']
    empty_bricks_count = len(list_of_empty_drives)

    if (not empty_bricks_count) or (empty_bricks_count % disperse_count):
        glogger.warning(f'Number of empty bricks: {empty_bricks_count}')
        return False

    return True


def gluster_volume_is_ready_to_scale(vol_name, list_of_empty_drives):
    """Check if volume is ready to scale using new bricks.

    Input :
    vol_name - Name of the volume needs to be scaled.
    list_of_empty_drives - list of empty drives present on any node.
    In the format hostname:/dev/drive{1..n}

    return :
    True - If volume is ready to be scaled.
    False - If volume can not be scaled.
    """
    # if not gluster_check_volume_health(vol_name):
    #     return False
    try:
        if not gluster_check_volume_health(vol_name):
            glogger.error("Can not scale {vol_name}. Volume is not healthy ")
            return False

        vol_info = sc.gf_get_volume_info_xml(vol_name)
    except GfCommandFailed as e:
        glogger.exception(e.message)
        return False

    vol_config = sc.gf_get_volume_config(vol_info)
    if not gf_are_bricks_sufficient(vol_config, list_of_empty_drives):
        glogger.error("Can not scale {vol_name}. \
                    Not enough empty bricks: {empty_bricks_count} ")
        return False

    return True


def gf_max_empty_drive_on_node(empty_disks_on_hosts, vol_config):
    """Get maximum number of empty drives any host can have."""
    """
    Input:
    empty_disks_on_hosts: Dict of host to empty drive.
    vol_config: volume configuration
    return:
    max_bricks: int, maximum nuber of empty bricks
    """
    red_bricks = vol_config['redundancyCount']
    disperse_bricks = vol_config['disperseCount']
    number_of_empty_bricks = int(0)

    for host, bricks in empty_disks_on_hosts.items():
        number_of_empty_bricks += len(bricks)

    max_new_subvols = (number_of_empty_bricks / disperse_bricks)
    return max_new_subvols * red_bricks


def gf_host_has_max_empty_disks(empty_disks_on_hosts, host_name, vol_config):
    """To check if a host already has maximum number of empty drives.

    Input:
    empty_disks_on_hosts: Dict of host to list of empty drive.
    host_name: hostname on which we want to check
    vol_config: volume configuration
    return:
    True: host_name has maximum allowed empty drive
    False: host_name does not have maximum allowed empty drive.
    """
    max_new_bricks = gf_max_empty_drive_on_node(empty_disks_on_hosts,
                                                vol_config)
    curr_bricks = empty_disks_on_hosts[host_name]

    if len(curr_bricks) < max_new_bricks:
        return False
    else:
        return True


def gf_initialize_empty_disks_per_host(empty_disks_on_hosts,
                                        list_of_empty_drives):
    """Fill dictionary with host name and empty disks on those hosts.

    Input :
    empty_disks_on_hosts: dict containing hosts to list of empty bricks.
    list_of_empty_drives: list of empty drives

    output:
    Sets the empty_disks_on_hosts with respective empty drives on existing host
    At the start this will only fill new node with new disks
    """
    for brick in list_of_empty_drives:
        host_brick = brick.split(':', 1)
        empty_disks_on_hosts[host_brick[0]].append(host_brick[1])

    for host, brick in empty_disks_on_hosts.items():
        glogger.info(f'host = {host}: empty disks = {brick}')


def gluster_create_brick_map_to_swap(vol_name="", new_host="",
    list_of_empty_drives=[]):
    """Get map of bricks which need to be replaced for scaling.

    Input :
    vol_name - Name of the volume which needs to be scaled.

    new_host - Hostname of the new node.

    list_of_empty_drives - list of empty drives present on any node
    in the format hostname:/dev/drive{1..n}.
    If we have swapped 2 empty drive and the application gets killed
    and we want to restart, we need to provide the list of all the
    empty drives even if the drives have been swapped. We have to
    provide new location of empty drives.

    Return :
    bricks_migration_map: List of named tuple. Each tuple containes
    old brick and new bricks which should be replaced.

    Example:
    Swap_bricks(old_brick='node-1:/root/brick-0-4', new_brick='node-4:/root/brick-12')

    """
    if not vol_name or not new_host or not list_of_empty_drives:
        glogger.debug(f'volume name = {vol_name} : new_host = {new_host}')
    #   return None

    bricks_migration_map = []
    empty_disks_on_hosts = collections.defaultdict(list)
    Swap_bricks = collections.namedtuple('Swap_bricks', ["old_brick", "new_brick"])

    # Get list of empty disks present on each node and create a dictionary
    gf_initialize_empty_disks_per_host(empty_disks_on_hosts, list_of_empty_drives)

    # *REMOVE ME* : just for testing, get it from file. Keep else part only
    if not vol_name:
        vol_info = test.gf_get_test_volume_info(subvol=6, data=4, red=2)
        for elm in vol_info["bricks_list"]:
            print (elm)
    else:
        vol_info = sc.gf_get_volume_info_xml(vol_name)

    vol_brick_list = sc.gf_get_volume_bricks_list(vol_info)

    vol_config = sc.gf_get_volume_config(vol_info)
    brcount = vol_config['disperseCount']

    subvol_brick_list = sc.gf_subvol_host_to_bricks_dict(vol_brick_list, brcount)

    if not gf_are_bricks_sufficient(vol_config, list_of_empty_drives):
        print("Not enough new drives to expend")
        return

    glogger.info(subvol_brick_list)
    # Add new_host in all the subvolume, we may have few bricks on this
    # host
    for subvol in subvol_brick_list:
        subvol[new_host] = []

    # start scanning subvol and whichever host has more than 1 brick for that subvol
    # pick that and see if that can be swapped to empty brick
    for subvol in subvol_brick_list:
        for host, bricks in subvol.items():

            if host == new_host:
                continue

            # Check if this host already have enough new disks and we can
            # not have any more new disks on this host
            if gf_host_has_max_empty_disks(empty_disks_on_hosts, host, vol_config):
                continue

            # Check if this host has enough old bricks on this host to replace
            if not len(bricks) > 1:
                continue

            # Check if this subvolume already have "redundancy" number of
            # bricks on new node
            if not len(subvol[new_host]) < vol_config['redundancyCount']:
                continue

            newbr = empty_disks_on_hosts[new_host].pop()
            oldbr = bricks.pop()

            # Add old brick to new host "new_host" of the subvol
            subvol[new_host].insert(0, oldbr)

            # Add new brick to old "host" of the subvol
            empty_disks_on_hosts[host].insert(0, newbr)

            oldbr = host + ":" + oldbr
            newbr = new_host + ":" + newbr

            # Add old and new bricks, with new_host, to swap map as named tuple
            swap = Swap_bricks(old_brick=oldbr, new_brick=newbr)
            bricks_migration_map.append(swap)

    return bricks_migration_map


def gluster_volume_commit_drive_swap(volname, old_brick, new_brick):
    """Commit changes to gluster EC volume.

    Input :
    vol_name - Name of the volume needs to be scaled.
    swap_map - This is the map/table of physically swapped drives.
    return :
    True - Commit passed
    False - Commit failed
    """
    cmd = "gluster v replace-brick " + volname + " " + old_brick + " " + new_brick + " commit force"
    ret, output, err = sc.run_gluster_command(cmd)

    return ret
