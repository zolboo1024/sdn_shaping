#!/usr/bin/env python2
import controller_CLI as cli
import time
from scapy.all import sniff, hexdump
import sys
import os

shaping = False

def shape(rates, duration):
	# Build the CLI
	sswitch_cli = cli.build_runtime_CLI()
	controller = cli.MyController(sswitch_cli)
	controller.table_delete("ipv4_lpm", "0")
	controller.table_add("ipv4_lpm", "ipv4_forward", ["10.0.1.3/32"], [3])
	controller.table_add("apply_shaping", "cloneThis", ["4"], [])
	controller.table_add("apply_shaping", "cloneThis", ["0"], [])
	# meter_array_set_rates
	controller.meter_array_set_rates_line("my_meter "+rates)
	time.sleep(duration)
	controller.table_delete("apply_shaping","0")
	controller.table_delete("apply_shaping","1")
	#controller.table_add("ipv4_lpm", "ipv4_forward", ["10.0.1.3/32"], [4])

def set_up_to_listen():
	# Build the CLI
	sswitch_cli = cli.build_runtime_CLI()
	controller = cli.MyController(sswitch_cli)
	controller.table_add("ipv4_lpm", "ipv4_forward", ["10.0.1.3/32"], [4])
	os.system("simple_switch_CLI --thrift-port 9090 < s1-rest.txt")

def handle_pkt(pkt):
	global shaping
	if shaping == False:
		print("RECEIVED HEREEEEEEEEEEEEEEEEEEE")
		if len(pkt) == 512:
			shape("0.0001:1 0.0001:1", 5)
		shaping = True

def main():
	set_up_to_listen()
	sys.stdout.flush()
	sniff(iface = "veth6", prn = lambda x: handle_pkt(x))

if __name__ == "__main__":
	main()
