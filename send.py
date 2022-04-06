#!/usr/bin/env python
import argparse
import sys
import socket
import random
import struct
import time
from threading import Thread
from scapy.all import sendp, send, get_if_list, get_if_hwaddr
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP

def createMessage(n):
    toRet = ""
    for i in range(n):
        toRet += "x"
    return toRet

def eachEvent(nums, slep, msgSize):
    startTime = time.time()
    threads = []
    for i in range(nums):
        thread = Thread(target = sendPacket, args = ("1",createMessage(msgSize),))
        thread.start()
        threads.append(thread)
        time.sleep(slep)
    for thread in threads:
        thread.join()
    duration = time.time()-startTime
    print("")
    print("-----Event report: {b} pkt/s for {d} seconds------".format(b=str(nums/duration),d=str(duration)))
    print("")
	
def event(eventID):
    global totalPacketsSent
    global startTime
    if eventID == 1:
    	print("")
    	print("____Starting event 1____")
    	print("")
    	eachEvent(15,0.3,100)
    elif eventID == 2:
    	print("")
    	print("____Starting event 2____")
    	print("")
    	eachEvent(23,0.2,120)
    elif eventID == 3:
    	print("")
    	print("____Starting event 3____")
    	print("")
        eachEvent(50,0.002,10)
    elif eventID == 4:
    	print("")
    	print("____Starting event 4____")
    	print("")
        eachEvent(50,0.008,20) 
            
def sendPacket(sourceIP, msg):
    addr = "10.0.1.3"
    iface = "veth"+sourceIP
    pkt =  Ether(src=get_if_hwaddr(iface), dst='00:00:00:00:00:01')
    pkt = pkt /IP(src="10.0.1."+str(sourceIP),dst=addr) / UDP(dport=1234, sport=random.randint(49152,65535)) / msg
    print("...sent packet of size "+str(len(bytes(pkt)))+"...")
    sendp(pkt, iface=iface, verbose=False)


if __name__ == '__main__':
    event(int(sys.argv[1]))
