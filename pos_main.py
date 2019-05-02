"""This script facilitates plus one scaling for disperse volume."""


import os
import scale.gf_plus_one_scale as sc
import test_data.gf_plus_one_test_data as test
from scale.gf_logs import glogger
from scale.gf_exceptions import (VolumeNotHealthy,
                                 GfCommandFailed)
from scale.gf_api import (gluster_volume_is_ready_to_scale,
                          gf_are_bricks_sufficient,
                          gluster_volume_is_ready_to_scale,
                          gluster_create_brick_map_to_swap,
                          gluster_volume_commit_drive_swap,
                          gluster_check_volume_health,
                          gluster_check_bricks_status)

def yes(value):
    """Return True if value is Y or Yes in any case."""
    return value.lower() in ["y", "yes"]


def gf_get_volume_and_bricks():
    """Get volume name, new node and file name from user."""
    volname = input("Enter name of the volume: ")
    filename = input("Enter file name which contains new bricks: ")
    hostname = input("Enter IP/hostname of new node: ")

    if not volname or not filename or not hostname:
        glogger.debug(f'Invalid user input: volname = {volname}, filename = {filename}, hostname = {hostname}')
        raise ValueError("volname or filename or hostname is not correct")

    return volname, filename, hostname


def gluster_volume_commit_all(volname, bricks_migration_map):
    """Commit physical replacment of all the bricks.

    Input:
    volname: Name of the volume
    bricks_migration_map: Physical migration map of old and new bricks.
    """
    for old_brick, new_brick in bricks_migration_map:
        glogger.info(f'Commiting replace bricks for old_brick = {old_brick} and new_brick = {new_brick}')
        print(f'Commiting replace bricks for old_brick = {old_brick} and new_brick = {new_brick}')
        try:
            gluster_volume_commit_drive_swap(volname, old_brick, new_brick)
        except GfCommandFailed as er:
            glogger.exception(f'replace brick failed for {old_brick} and {new_brick}')
            continue
        else:
            glogger.info(f'replace brick is done for {old_brick} and {new_brick}')


def gf_swap_all_bricks(volname, bricks_migration_map):
    """Swap all the bricks.

    This function helps to swap all the bricks first and then commit
    the physical migration in one shot.
    Input:
    volname: Name of the volume
    bricks_migration_map: Physical migration map of old and new bricks.
    """
    while True:
        print("Swap following disks : ")
        for br in bricks_migration_map:
            print(br)
        done = input("Have you finished swapping all the disks: (y/n) ")
        if yes(done):
            gluster_volume_commit_all(volname, bricks_migration_map)
        else:
            continue


def gf_swap_one_by_one_brick(volname, bricks_migration_map):
    """Swap bricks one by one.

    Ask user to swap a pair of old and new brick and then
    commit that migration
    Input:
    volname: Name of the volume
    bricks_migration_map: Physical migration map of old and new bricks.
    """
    for old_brick, new_brick in bricks_migration_map:
        while True:
            try:
                print(f'Swap {old_brick} and {new_brick}')
                done = input("Have you finished swapping above disks: (y/n) ")
                if yes(done):
                    gluster_volume_commit_drive_swap(volname, old_brick, new_brick)
                    break
                else:
                    continue
            except GfCommandFailed as er:
                        glogger.exception(f'replace brick failed for {old_brick} and {new_brick}')
                        continue
            else:
                glogger.info(f'replace brick is done for {old_brick} and {new_brick}')


def gf_migrate_bricks_using_swap_map(volname, bricks_migration_map):
    """Swap bricks using migration map.

    Ask user how the migration should happen.
    Input:
    volname: Name of the volume
    bricks_migration_map: Physical migration map of old and new bricks.
    """
    while True:
        try:
            print("All together : 1")
            print("One brick at a time : 0")
            all = int(input("How do you want to swap device: (0 or 1) "))
            if all not in [0, 1]:
                print("Please enter correct option.")
                continue
            else:
                break
        except:
            print("Please enter valid option")
            glogger.debug(f'Invalid swap option, enter an interger (0/1)')
            done = input("Want to exit? y/N")
            if yes(done):
                exit(1)

    if (all):
        gf_swap_all_bricks(volname, bricks_migration_map)
    else:
        gf_swap_one_by_one_brick(volname, bricks_migration_map)


def main():
    """Main function to start complete plus one scaling process."""
    while True:
        try:
            volname, filename, hostname = gf_get_volume_and_bricks()
        except ValueError as er:
            print(er)
            glogger.exception(er)
        else:
            print(f'volname = {volname}')
            print(f'filename = {filename}')
            print(f'hostname = {hostname}')
            break
    try:
        list_of_empty_drives = sc.gf_get_new_bricks_list(filename)
        print ("**************New Bricks*****************")
        for br in list_of_empty_drives:
            print(br)
        print ("****************************************")
    except GfCommandFailed as e:
        print(e.message)
        exit(1)

    if not gluster_volume_is_ready_to_scale(volname, list_of_empty_drives):
        print(f'EC volume, {volname}, can not be scaled. Volume not healthy or all the bricks are not UP')
        exit(1)
    else:
        print(f'{volname} can be scaled')

    print ("****************************************")
    bricks_migration_map = gluster_create_brick_map_to_swap(
        vol_name=volname, new_host=hostname,
        list_of_empty_drives=list_of_empty_drives)

    for old, new in bricks_migration_map:
        print (f'old_brick={old} and new brick={new}')

    gf_migrate_bricks_using_swap_map(volname, bricks_migration_map)


if __name__ == "__main__":
    main()
