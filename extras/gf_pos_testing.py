from test_data.gf_plus_one_test_data import *
from scale.gf_plus_one_scale import *

# Test code
def test():
	print ("***********************************************************")	
	fname = create_new_node(12,4)
	v_info = gf_bricks_from_file(fname)
	for br in v_info:
		print(br)
	
	print ("***********************************************************")	

	fname  = create_gluster_v_info(6,4,2)
	v_info = gf_bricks_from_file(fname)

	for br in v_info:
		print(br)

	print ("***********************************************************")
	
	print ("volume_brick_list")
	node_brick_list = gf_get_volume_bricks_list(v_info)
	print (node_brick_list)
	for elm in node_brick_list:
		print (elm)


	print ("***********************************************************")
	print ("node_brick_dict")
	node_brick = gf_get_node_bricks_dict(v_info)
	for key,val in node_brick.items():
		print (key, val)
		print ('\n')

	print ("***********************************************************")
	print ("subvol_brick_list")
	node_b = gf_get_volume_bricks_list(v_info)

	subvol_brick_list = gf_subvol_bricks_dict(node_b, 6)
	count = 0
	for elm in subvol_brick_list:
		print("ec -subvolume-"+ str (count))
		print(elm)
		count += 1 

	print ("***********************************************************")
'''
	print ("Volume info")
	volume_info = gf_get_volume_info ('vol')
	for elm in volume_info:
		print (elm)

	print ("***********************************************************")

	print ("Volume config")
	volume_config = gf_get_volume_config(volume_info)
	print (volume_config)


	print ("***********************************************************")

	print ("volume_brick_list")
	node_brick_list = gf_get_volume_bricks_list(volume_info)
	for elm in node_brick_list:
		print (elm)


	print ("***********************************************************")


	print ("node_brick_dict")
	node_brick = gf_get_node_bricks_dict(volume_info)
	for key,val in node_brick.items():
		print (f"Host = {key} bricks = {val}")


	print ("***********************************************************")

	print ("subvol_brick_list")
	subvol_brick_list = gf_subvol_bricks_list(volume_info)
	count = 0
	for elm in subvol_brick_list:
		print("ec -subvolume-"+ str (count))
		print(elm)
		count += 1 
	print ("***********************************************************")
'''


if True:
	test()







