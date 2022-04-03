#!/usr/bin/env python2

from sswitch_CLI import SimpleSwitchAPI
import runtime_CLI #as api

# This is the test controller for this simulation
# Not quite sure whether it can finally use in the test.

# Build the CLI connection
def build_runtime_CLI():
	args = runtime_CLI.get_parser().parse_args()
	args.pre = runtime_CLI.PreType.SimplePreLAG
	services = runtime_CLI.RuntimeAPI.get_thrift_services(args.pre)
	services.extend(SimpleSwitchAPI.get_thrift_services())

	standard_client, mc_client, sswitch_client = runtime_CLI.thrift_connect(
		args.thrift_ip, args.thrift_port, services
	)
	runtime_CLI.load_json_config(standard_client, args.json)
	sswitch_cli = SimpleSwitchAPI(args.pre, standard_client, mc_client, sswitch_client)
	return sswitch_cli

class MyController:
	def __init__(self, sswitch_client):
		self.client = sswitch_client

	def connect(self):
		self.client.cmdloop()

	def table_add(self, table_name, action, keys, arguments):
		# table_add table_name action keys [other_keys] => arguments [other_args]
		line = table_name + " " + action + " "
		for key in keys:
			line += (key + " ")

		line = line + "=> "
		for arg in arguments:
			line += (arg + " ")

		self.client.do_table_add(line)

	def table_add(self, line):
		self.client.do_table_add(line)



	def test_table_add(self):
		line = "ipv4_lpm ipv4_forward 1 1 => 1"
		self.client.do_table_add(line)

if __name__ == "__main__":
	
	sswitch_cli = build_runtime_CLI()
	controller = MyController(sswitch_cli);

	#controller.connect()
	controller.test_table_add()
		
