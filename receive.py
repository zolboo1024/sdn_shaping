#!/usr/bin/env python
import sys
#import struct
#import os
import time
import atexit
from scapy.all import sniff, hexdump
#from scapy.all import Packet, IPOption
#from scapy.all import IP, TCP, UDP, Raw

firstPacketTime = 0
numReceived = 0 

def handle_pkt(pkt):
	global firstPacketTime
	global numReceived
	print("Received packet of size: "+str(len(pkt)))
	if firstPacketTime == 0:
		firstPacketTime = time.time()
	numReceived += 1


def main():
	global firstPacketTime
	global numReceived	
 	iface = sys.argv[1]
	print "sniffing on %s" % iface
 	sys.stdout.flush()
 	sniff(iface = iface, prn = lambda x: handle_pkt(x), timeout=5)
	lastPacketTime = time.time()
	diff = lastPacketTime - firstPacketTime
	print("")
	print("")
	print("Number of pkts/sec: "+str(numReceived/diff))
	print("")

def exit_handler():
	global firstPacketTime
	global numReceived	
	lastPacketTime = time.time()
	diff = lastPacketTime - firstPacketTime
	print("")
	print("")
	print("Number of pkts/sec: "+str(numReceived/diff))
	print("")
	atexit.register(exit_handler)

if __name__ == '__main__':
    main()
