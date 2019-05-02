Gluster Plus One Scaling
==============================
To increase the capacity of existing gluster volume (AFR or EC), we need to add more bricks on that volume. Currently, it is needed to distribute these bricks on as many nodes as it requires to keep the volume fault tolerant. This depends on the configuration of the volume. This in turn requires adding more than 1 node to scale gluster volume. However, it is not always possible to buy and place lot of nodes/servers in one shot and add these nodes into cluster to scale our volume. To solve this, we have to come up with some solution so that we can scale out volume even if we add one server with enough bricks on that one server.
This tools helps user to facilitate scaling of a disperse volume by one node only if there are enough number of bricks available on that node.


Usage
==============================
python3 pos_main.py