#!/usr/bin/env python2
import controller_CLI as cli
import time

def test_examples1():
	# Build the CLI
	sswitch_cli = cli.build_runtime_CLI()
	controller = cli.MyController(sswitch_cli);
	
	# table_set_default
	controller.table_set_default(table_name = "ipv4_lpm", action = "drop")

	# table_add
	controller.table_add(table_name = "ipv4_lpm", action = "ipv4_forward", keys = ["10.0.1.1/32"], parameters = [3])
	controller.table_add("ipv4_lpm", "ipv4_forward", ["10.0.1.2/32"], [3])
	controller.table_add("ipv4_lpm", "ipv4_forward", ["10.0.1.3/32"], [3])

	controller.table_add("m_read", "m_action", ["10.0.1.3"]) # If no parameters in the action, you can leave it blank
	controller.table_add("m_filter", "NoAction", [0])
	controller.table_add("m_filter", "NoAction", [1])
	controller.table_add("apply_shaping", "cloneThis", ["4"])
	controller.table_add("apply_shaping", "cloneThis", ["1"])

	# meter_array_set_rates
	controller.meter_array_set_rates(meter_name = "my_meter", rates = [0.0000005, 0.00001], bursts = [1,1])
	# set_queue_rate
	controller.set_queue_rate(rate_pps = 1000, egress_port = 3)
	# mirroring_add
	controller.mirroring_add(mirror_id = 5, egress_port = 4)

def test_examples2():
	# Build the CLI
	sswitch_cli = cli.build_runtime_CLI()
	controller = cli.MyController(sswitch_cli);
	
	# table_set_default
	# table_set_default ipv4_lpm drop
	controller.table_set_default_line(line = cli.generate_line(["ipv4_lpm", "drop"]))

	# table_add
	# table_add MyIngress.ipv4_lpm ipv4_forward 10.0.1.1/32 => 3
	# table name and action
	basic_line = cli.generate_line(["ipv4_lpm", "ipv4_forward"])
	# match keys part
	line = cli.concat_line(basic_line, ["10.0.1.1/32"])
	# action parameters part
	line = cli.concat_line(line, ["=>", 3])
	# execute
	controller.table_add_line(line)

	# table_add m_read m_action 10.0.1.3 =>
	# table name and action 
	basic_line = cli.generate_line(["m_read", "m_action"])
	# match keys (without parameters)
	line = cli.concat_line(basic_line, ["10.0.1.3", "=>"]) # You can add the => to the keys here
	# execute
	controller.table_add_line(line)

	# meter_array_set_rates
	# meter_array_set_rates my_meter 0.0000005:1 0.00001:1
	controller.meter_array_set_rates_line("my_meter 0.0000005:1 0.00001:1")
	# set_queue_rate
	# set_queue_rate 1000 3
	controller.set_queue_rate_line("1000 3")
	# mirroring_add
	# mirroring_add 5 4
	controller.mirroring_add_line("5 4")

def test_table():
	# Build the CLI
	sswitch_cli = cli.build_runtime_CLI()
	controller = cli.MyController(sswitch_cli);

	# Test 1: Default mark drop and to port 2 and to port 3
	# table_set_default
	# controller.table_set_default(table_name = "ipv4_lpm", action = "drop")
	# time.sleep(10)
	# controller.table_set_default(table_name = "ipv4_lpm", action = "ipv4_forward", parameters = [2])
	# time.sleep(10)
	# controller.table_set_default(table_name = "ipv4_lpm", action = "ipv4_forward", parameters = [3])
	# time.sleep(30)

	# Test 2: Add a table entry to 1 and set timeout 10s
	# Handle 1
	entry_handle1 = controller.table_add("ipv4_lpm", "ipv4_forward", ["10.0.1.3/32"], [2])
	print entry_handle1
	controller.table_set_timeout("ipv4_lpm", entry_handle1, 10000)

	time.sleep(15)
	controller.table_delete("ipv4_lpm", entry_handle1)

	# Test 3: Modify old entry from 1 to 2
	entry_handle2 = controller.table_add("ipv4_lpm", "ipv4_forward", ["10.0.1.3/32"], [1])
	controller.table_modify("ipv4_lpm", "ipv4_forward", entry_handle2, [2])

	time.sleep(15)

	# Test 4: Delete entry
	controller.table_delete("ipv4_lpm", entry_handle2)

def main():
	# Test 1: Users import parameters directly to do commands.
	# test_examples1()

	# Test 2: Users generate CLI-like sentences to do commands
	# test_examples2()

	# Test 3: Test the function of
	# table_set_default, table_add, table_delete, 
	# table_set_timeout, table_modify
	test_table()

if __name__ == "__main__":
	main()
