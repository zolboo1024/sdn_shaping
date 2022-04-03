#!/usr/bin/env python
import sys
#import struct
import os
import time
import atexit
from scapy.all import sniff, hexdump
#from scapy.all import Packet, IPOption
#from scapy.all import IP, TCP, UDP, Raw

shapingRN = False
firstPacketTime = 0
numReceived = 0 

def handle_pkt(pkt):
    global shapingRN
    if (shapingRN==False):
        shapingRN==True
        #start the shaping
        os.system("sudo simple_switch_CLI --thrift-port 9090 < ./commands/event1Start.txt")
        time.sleep(10)
        os.system("sudo simple_switch_CLI --thrift-port 9090 < ./commands/end.txt")

def main():
    #veth8 (5 at the switch) is reserved for the controller
    iface = 'veth8'
    print "sniffing on %s" % iface
    sys.stdout.flush()
    sniff(iface = iface,
          prn = lambda x: handle_pkt(x))

def exit_handler():
	global firstPacketTime
	global numReceived	
	lastPacketTime = time.time()
	diff = lastPacketTime - firstPacketTime
	print(str(numReceived/diff))

atexit.register(exit_handler)

if __name__ == '__main__':
    #start the switch
    os.system("sudo simple_switch_CLI --thrift-port 9090 < ./commands/baseCommands.txt")
    main()
