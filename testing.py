from test_data.gf_plus_one_test_data import *
from scale.gf_plus_one_scale import *
from scale.gf_api import *
from scale.gf_logs import *


# Test code to test scripts.
def test():
    if not gluster_check_volume_health('vol'):
        print (f'vol is not healthy')


def getmap():

    list_of_empty_drives = gf_test_get_new_bricks("node-4", 12)
    print ("list of empty bricks")
    for br in list_of_empty_drives:
        print (br)
    print("\n\n")

    bricks_replace_map = gluster_create_brick_map_to_swap("", "node-4", list_of_empty_drives)

    print("\n\n")
    if bricks_replace_map:
        for br_map in bricks_replace_map:
            print(br_map)


if True:
    test()
    getmap()
    # gf_xml_status()
    #print(gf_get_test_volume_info(subvol=12, data=4, red=2))
