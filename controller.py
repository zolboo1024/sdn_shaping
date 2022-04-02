# Test

from p4utils.utils.sswitch_p4runtime_API import SimpleSwitchP4RuntimeAPI

# This is the test controller for this simulation
# Not quite sure whether it can finally use in the test.
class MyController:
	def __init__(self, device_id=0, port=9090, ip='0.0.0.0', json_file=None):
		self.device_id = device_id
		self.port = port
		self.ip = ip
		self.json_file = json_file
		self.controller = SimpleSwitchP4RuntimeAPI(
			device_id = self.device_id,
			grpc_port = self.port,
			grpc_ip = self.ip,
			json_path = self.json_file)

	def start(self):

		return 0

if __name__ == "__main__":
	controller = MyController(port = 9090)
	controller.start()
		
