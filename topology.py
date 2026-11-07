from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def create_network():
    net = Mininet(
        controller=None,
        switch=OVSSwitch,
        autoSetMacs=True
    )

    info("*** Ajout du controleur Ryu\n")
    c0 = net.addController(
        'c0',
        controller=RemoteController,
        ip='127.0.0.1',
        port=6653
    )

    info("*** Creation des machines\n")
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')

    info("*** Creation du switch SDN\n")
    s1 = net.addSwitch(
        's1',
        protocols='OpenFlow13',
        failMode='secure'
    )

    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)

    info("*** Demarrage du reseau\n")
    net.start()

    info("*** Interface Mininet\n")
    CLI(net)

    info("*** Arret du reseau\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_network()
