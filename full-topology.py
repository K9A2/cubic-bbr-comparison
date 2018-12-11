#!/usr/bin/python
# coding=utf-8

import os
import time

from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.topo import Topo

import libstorm as storm


loss = [0.01, 0.10, 1.00]
rtt = [30, 100, 200]

algorithm = 'cubic'

max_test_count = 120
# Tests conducted in each group
step = 10
# The start point of each group
group_start = []

i = 0
while i < max_test_count:
    group_start.append(i)
    print i
    i += step

tcpdump_command_template = \
    'tcpdump -i %s-eth0 tcp 1> ./tcpdump-%s-rtt%s-loss%s-1g-%s.log &'
shell_command_template = './run.sh -c %s -a %s -r %s -l %s -s %s -e %s 1> %s &'


class FullTopology(Topo):

    def __init__(self):
        Topo.__init__(self)

        # set up the topology according loss and rtt specified
        j = 0
        for r in rtt:
            for l in loss:
                for i in range(0, len(group_start)):
                    # the name of sender and receiver hosts
                    sender_name = 'h' + str(j) + '-1'
                    receiver_name = 'h' + str(j) + '-2'

                    sender_switch_name = 's' + str(j) + '-1'
                    receiver_switch_name = 's' + str(j) + '-2'

                    j += 1

                    # add hosts and switches
                    sender = self.addHost(sender_name)
                    sender_switch = self.addSwitch(sender_switch_name)
                    receiver = self.addHost(receiver_name)
                    receiver_switch = self.addSwitch(receiver_switch_name)

                    # connect the devices and create bottleneck
                    self.addLink(sender, sender_switch,
                                 bw=1000, delay=str(r / 6) + 'ms', loss=0)
                    self.addLink(sender_switch, receiver_switch,
                                 bw=100, delay=str(r / 6) + 'ms', loss=l)
                    self.addLink(receiver_switch, receiver,
                                 bw=1000, delay=str(r / 6) + 'ms', loss=0)


def run():

    net = Mininet(topo=FullTopology(), host=CPULimitedHost, link=TCLink)
    net.start()

    # configure the network and run the test
    j = 0
    for r in rtt:
        for l in loss:
            for i in range(0, len(group_start)):
                sender_name = 'h' + str(j) + '-1'
                receiver_name = 'h' + str(j) + '-2'

                j += 1

                sender = net.get(sender_name)
                receiver = net.get(receiver_name)

                # disable tso at all hosts
                sender.cmd('ethtool -K ' + sender_name + '-eth0 tso off')
                receiver.cmd('ethtool -K ' + receiver_name + '-eth0 tso off')

                time.sleep(3)

                # run iperf3 daemon at the receiver
                receiver.cmd('iperf3 -s -D')

                storm.log('sleep 3s to run the test')
                time.sleep(3)

                # run the test
                sender.cmd(shell_command_template % (
                    # network information
                    algorithm, receiver.IP(), str(r), str(l),
                    # the start round and end round of this group
                    str(group_start[i]), str(group_start[i] + step),
                    # log file name
                    algorithm + '-runtime-rtt' + str(r) + '-loss' + str(l) +
                    '-' + str(i) + '.log'
                ))

                storm.log(algorithm + ': rtt' + str(r) + '-loss' + str(l) +
                          '-' + str(i) + '-' + str(group_start[i]) + '-' +
                          str(group_start[i] + step) + ' started')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    # clear potential dangling network NICs before setting up the new network
    os.system('mn -c')
    setLogLevel('info')
    run()
