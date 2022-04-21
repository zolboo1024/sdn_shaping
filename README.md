# SDN-based Traffic Shaping
Repo for the SDN class project
## Packet Padding
To save packet sizes from inference, we first need to pad all packets

Therefore, we implemented a version of packet padding.

Concretely, there are headers of different sizes, and provided a new size, these headers are added to reach the provided size. 

`padding.p4` implements this approach to shaping. To test it, we can build/emulate the same topology as we did in class:

```
$ p4c-bm2-ss padding.p4 -o padding.json
$ sudo simple_switch -i 0@veth0 -i 1@veth2 --log-console padding.json
$ sudo simple_switch_CLI --thrift-port 9090 < switch_config
```
Then, send packets using `send.py`. It prints out the size of all the packets sent.

As you receive the packets using `receive.py`, it prints out the size of the packets received. You can notice that no matter what size packet is sent, it is padded to 512 bytes. 

You can modify the new packet size using the `padTo` variable in `myIngress`.

## Dummy Packet Insertion and Rate Control

To achieve constant rate traffic, we must inject packets at periods where the device sends no traffic.

Our solution to dummy packet injection consists of 2 parts: cloning and recirculating.

We use the cloning function native to `bmv2`. In particular, we choose the `CloneType.I2E` flag to send cloned traffic from the ingress
port to the egress port 5.

Then, once the packet arrives at port 5, we send the cloned packet back to the ingress to recirculate. We know that such packets 
are cloned using the field `instance_type` in the `standard_metadata` headers. We use the function `recirculate` function native `bmv2`. 

The final piece to achieve the constant rate in traffic is to rate limit the dummy packet insertion while prioritizing real packets.

To prioritize real packets, we use 2 of the 7 prioritiy queues provided by the `bmv2` switch. However, multi-queueing must be "activated"
in order to be used.

### Important
### To activate multi-queues on your instance on `bmv2`, please follow the instructions on here: [link](https://github.com/nsg-ethz/p4-learning/tree/master/examples/multiqueueing)

Then, we put the real packets in queue 7 as the highest priority packets and the dummy ones in queue 0 as the lowest priority packets. Then,
whenever real packets arrive at the switch, it is sent while dummy packets are dropped. 

Finally, we use 2 rate 3 color rate limit algorithm provided natively by `bmv2` to keep traffic at a constant rate. In particular, we use the `meter_tag` in `meta` headers of the arrive packets to tag packets to be dropped if it goes over the specified limit. More information on `bmv2 meter` can be found here: [link](https://github.com/nsg-ethz/p4-learning/tree/master/examples/meter)

## Testing our Solution

We prepared test cases for you to test our solution. In particular, `./send.py` sends flows of different rates as specified in the report. You must specify which event you would like to run as an argument. For example, `sudo ./send.py 1` emulates event 1. Event 1 and 2 are low bandwidth while Event 3 and 4 are high bandwidth. 

To activate the controller, we must also run `./test_controller.py`. As the controller is initialized, we also set up the initial forwarding rules to make sure that the packets are forwarded correctly.

You must also run `./receive.py` to receive packets after events have been shaped. After shaping, you may notice that Event 1 and 2 are transformed into the same shape while Event 3 and 4 are transformed to another.

Finally, don't forget to run `./veth_setup.sh`. This is the same script provided by Miguel. 

Overall, here's a list of commands you can use to test our solution:

```
$ sudo ./veth_setup.sh
$ p4c-bm2-ss multi_queueing.p4 -o multi_queueing.json
$ sudo simple_switch -i 0@veth0 -i 1@veth2 2@veth4 3@veth6 4@veth8 --log-console multi_queueing.json   (start the swtich)
$ sudo ./test_controller.py    (configure the switch and start the controller)
$ sudo ./receive.py            (listen to outgoing traffic from the switch)
$ sudo ./send.py 1             (send events)
```
Please restart the process to test different events. You will notice that Events 1 and 2 are transformed to 10 pkts/s shape and Events 3 and 4 are transformed to 80 pkts/s shape. Finally, you will also notice that all packets are padded to the same size and this size is determined dynamically by the switch. 


