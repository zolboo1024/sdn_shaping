import nnpy
import struct
from scapy.all import sniff, Packet, BitField, raw

from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_p4runtime_API import SimpleSwitchP4RuntimeAPI
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from scapy.layers.l2 import Ether
from scapy.sendrecv import sendp


class CpuInHeader(Packet):
    name = "cpu_in"
    fields_desc = [
        BitField("ingress_port", 0, 9),
        BitField("_pad", 0, 7)
    ]


class CpuOutHeader(Packet):
    name = "cpu_out"
    fields_desc = [
        BitField("egress_port", 0, 9),
        BitField("_pad", 0, 7)
    ]

class CpuController:

    def __init__(self, sw_name):
        self.topo = load_topo('topology.json')
        self.sw_name = sw_name
        self.cpu_port_intf = 0
        self.cpu_port = self.topo.get_cpu_port_index(self.sw_name)
        device_id = self.topo.get_p4switch_id(sw_name)
        grpc_port = self.topo.get_grpc_port(sw_name)
        sw_data = self.topo.get_p4rtswitches()[sw_name]
        self.controller = SimpleSwitchP4RuntimeAPI(device_id, grpc_port,
                                                   p4rt_path=sw_data['p4rt_path'],
                                                   json_path=sw_data['json_path'])
        self.init()

    def init(self):
        self.reset()

    def reset(self):
        self.controller.reset_state()
        thrift_port = self.topo.get_thrift_port(self.sw_name)
        controller_thrift = SimpleSwitchThriftAPI(thrift_port)
        controller_thrift.reset_state()

    def add_clone_session(self):
        if self.cpu_port:
            self.controller.cs_create(100, [self.cpu_port])

    def deal_pack(self, pack):
        ingress_port = pack.ingress_port
        if ingress_port == 1:
            egress_port = 2
        else:
            egress_port = 1
        send_pack = CpuOutHeader()
        send_pack.payload = pack.payload
        mac_pack = Ether(raw(send_pack.load))
#        mac_pack.show()
        send_pack.egress_port = egress_port
        send_pack._pad = 0
#        send_pack.show()
        return send_pack

    def send_msg_cpu(self, pack):

        sendp(pack, iface=self.cpu_port_intf, verbose=False)

    def recv_msg_cpu(self, pkt):
        pack = CpuInHeader(raw(pkt))
        #print("this is receive")
        #pack.show()
        pack = self.deal_pack(pack)
        #print("this is send")
        #pack.show()
        mac = Ether(raw(pack.payload))
        mac.show()
        #print('send a packet')
        #self.send_msg_cpu(pack)

    def run_cpu_port_loop(self):
        self.cpu_port_intf = str(self.topo.get_cpu_port_intf(self.sw_name).replace("eth0", "eth1"))
        sniff(iface = self.cpu_port_intf, prn = self.recv_msg_cpu)

if __name__ == "__main__":
    CpuController('s1').run_cpu_port_loop()
#bind_layers(Ether, MyTunnel, type=TYPE_MYTUNNEL)
#bind_layers(MyTunnel, IP, pid=TYPE_IPV4)
