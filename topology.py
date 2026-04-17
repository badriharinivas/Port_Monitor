#!/usr/bin/env python3
"""
topology.py - Mininet topology that connects to the Ryu controller
"""
from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.cli import CLI

class MonitorTopo(Topo):
    def build(self):
        s1 = self.addSwitch('s1')

        h1 = self.addHost('h1', ip='10.0.0.1/24')
        h2 = self.addHost('h2', ip='10.0.0.2/24')
        h3 = self.addHost('h3', ip='10.0.0.3/24')
        h4 = self.addHost('h4', ip='10.0.0.4/24')

        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(h4, s1)

def run():
    setLogLevel('info')
    topo = MonitorTopo()
    # RemoteController connects to Ryu running on localhost:6633
    net = Mininet(
        topo=topo,
        switch=OVSSwitch,
        controller=lambda name: RemoteController(name, ip='127.0.0.1', port=6633)
    )
    net.start()
    print("[*] Topology started. Connected to Ryu on port 6633.")
    CLI(net)
    net.stop()

if __name__ == '__main__':
    run()
