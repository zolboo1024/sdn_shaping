#!/usr/bin/env python
import argparse
import sys
import socket
import random
import struct
import time
from scapy.all import sendp, send, get_if_list, get_if_hwaddr
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP


def sendPacket(sourceIP):

    addr = "10.0.1.3"
    iface = "veth"+sourceIP

    print "sending on interface %s to %s" % (iface, str(addr))
    pkt =  Ether(src=get_if_hwaddr(iface), dst='00:00:00:00:00:01')
    pkt = pkt /IP(src="10.0.1."+str(sourceIP),dst=addr) / UDP(dport=1234, sport=random.randint(49152,65535)) / str(sourceIP)
    pkt.show2()
    sendp(pkt, iface=iface, verbose=False)


if __name__ == '__main__':
    while(True):
        time.sleep(1)
        sendPacket("1")
