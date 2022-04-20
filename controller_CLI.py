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

def generate_line(contents):
	line = ""
	for content in contents:
		line += (str(content) + " ")
	return line

def concat_line(origin_line, contents):
	line = origin_line
	for content in contents:
		line += (str(content) + " ")
	return line 

class MyController:
	def __init__(self, sswitch_client):
		self.client = sswitch_client

	def run_cli_in_cmd(self):
		self.client.cmdloop()

	def table_add(self, table_name, action, keys, parameters=[]):
		# table_add table_name keys => parameters
		# line = table_name + " " + action + " "
		# for key in keys:
		# 	line += (key + " ")

		# line = line + "=> "
		# for param in parameters:
		# 	line += (param + " ")
		line = generate_line([table_name, action])
		line = concat_line(line, keys)
		line = concat_line(line, ["=>"])
		line = concat_line(line, parameters)

		entry_handle = self.client.do_table_add(line)
		return entry_handle; 

	def table_set_default(self, table_name, action, parameters=[]):
		# table_set_default table_name action parameters
		# line = table_name + " " + action + " "

		# for param in parameters:
		# 	line += (param + " ")
		line = generate_line([table_name, action])
		line = concat_line(line, parameters)

		self.client.do_table_set_default(line)

	def mirroring_add(self, mirror_id, egress_port):
		# mirroring_add mirror_id egress_port
		# line = "" + mirror_id + " " + egress_port
		line = generate_line([mirror_id, egress_port])
		self.client.do_mirroring_add(line)

	def meter_array_set_rates(self, meter_name, rates, bursts):
		# meter_array_set_rates meter_name [rate:burst]
		line = meter_name + " "
		length = len(rates)
		for i in range(length):
			line += (str(rates[i]) + ":" + str(bursts[i]) + " ")
		self.client.do_meter_array_set_rates(line)

	def table_set_timeout(self, table_name, entry_handle, timeout=1000):
		# table_set_timeout <table_name> <entry handle> <timeout (ms)>
		# line = "" + table_name + " " + entry_handle + " " + timeout
		line = generate_line([table_name, entry_handle, timeout])
		self.client.do_table_set_timeout(line)

	def table_delete(self, table_name, entry_handle):
		# table_delete <table name> <entry handle>
		line = generate_line([table_name, entry_handle])
		# line = "" + table_name + " " + entry_handle
		self.client.do_table_delete(line)
	def table_modify(self, table_name, action_name, entry_handle, parameters=[]):
		# table_modify <table name> <action name> <entry handle> [parameters]
		line = generate_line([table_name, action_name, entry_handle])
		line = concat_line(line, parameters)
		# line = "" + action_name + " " + entry_handle + " "
		# for param in parameters:
		# 	line += (param + " ")
		self.client.do_table_modify(line)

	def set_queue_rate(self, rate_pps, egress_port=None):
		# set_queue_rate <rate_pps> [<egress_port>]
		line = generate_line([rate_pps])
		if egress_port is not None:
			line = concat_line(line, [egress_port])
		self.client.do_set_queue_rate(line)
	
	def set_queue_rate_line(self, line):
		self.client.do_set_queue_rate(line)

	def table_modify_line(self, line):
		self.client.do_table_modify(line)

	def table_delete_line(self, line):
		self.client.do_table_delete(line)

	def table_set_timeout_line(self, line):
		self.client.do_table_set_timeout(line)

	def meter_array_set_rates_line(self, line):
		self.client.do_meter_array_set_rates(line)

	def mirroring_add_line(self, line):
		self.client.do_mirroring_add(line) 	 

	def table_set_default_line(self, line):
		self.client.do_table_set_default(line)

	def table_add_line(self, line):
		entry_handle = self.client.do_table_add(line)
		return entry_handle;


def main():
	sswitch_cli = build_runtime_CLI()
	controller = MyController(sswitch_cli);
	# If you want to run the CLI in cmd, use this sentence
	controller.run_cli_in_cmd()

	
if __name__ == "__main__":
	main()
	
	

