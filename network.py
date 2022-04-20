from network_API import NetworkAPI

net = NetworkAPI()

# Network general options
net.setLogLevel('info')
net.enableCli()

# Network definition
net.addP4Switch('s1', cli_input='s1-commands.txt')
net.setP4Source('s1','multi_queueing.p4')
net.addHost('h1')
net.addHost('h2')
net.addHost('h3')

net.addLink('s1', 'h1')
net.addLink('s1', 'h2')
net.addLink('s1', 'h3', bw=5)

# Assignment strategy
net.mixed()

# Nodes general options
net.enablePcapDumpAll()
net.enableLogAll()

# Start network
net.startNetwork()