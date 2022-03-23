#!/usr/bin/env python
import sys
#import struct
#import os

from scapy.all import sniff, hexdump
#from scapy.all import Packet, IPOption
#from scapy.all import IP, TCP, UDP, Raw


def handle_pkt(pkt):
        print("packet size: "+str(len(pkt)))
        sys.stdout.flush()


def main():
    iface = 'veth2'
    print "sniffing on %s" % iface
    sys.stdout.flush()
    sniff(iface = iface,
          prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()
