# SDN-based Traffic Shaping
Repo for the SDN class project
## Packet Padding
To save packet sizes from inference, we first need to pad all packets
### 23/03/2022
Implemented a rudimentary version of traffic padding.

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

## Dummy Packet Insertion

In progress...
