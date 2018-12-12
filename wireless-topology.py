#!/usr/bin/python
# coding=utf-8

import getopt
import sys
import time

from mininet.node import Controller
# from mininet.node import RemoteController

from mn_wifi.cli import CLI_wifi
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP

import libstorm as storm


shell_command_template = './run.sh -c %s -a %s -f %s -s %s -e %s 1> %s &'


def usage():
    print 'Use this file the launch the evaluation in Wi-Fi environment'
    print ''
    print 'Usage wireless-topology [-a|--algorithm <algorithm>]'
    print '                        [-f|--frequency <frequency>]'
    print '                        [-m|--max-count <max-count>]'
    print '                        [-g|--group <group>]'
    print '                        [-h|--help]'
    print ''
    print 'You need to specify all arguments in command line'


def parse_arguments(argv, description):
    try:
        opts, args = \
            getopt.getopt(
                argv, 'ha:f:m:g:',
                ['help', 'algorithm=', 'frequency=', 'max-count=', 'group='])
    except getopt.GetoptError:
        print 'Error: Wrong argument(s)'
        usage()
        sys.exit()
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        if opt in ('-a', '--algorithm'):
            description['algorithm'] = arg
        if opt in ('-f', '--frequency'):
            description['frequency'] = arg
        if opt in ('-m', '--max-count'):
            description['max-count'] = int(arg)
        if opt in ('-g', '--group'):
            description['group'] = int(arg)


def main(argv):

    description = {}
    parse_arguments(argv, description)
    algorithm = description['algorithm']
    frequency = description['frequency']
    max_count = description['max-count']
    group = description['group']

    storm.log('algorithm: %s' % description['algorithm'])
    storm.log('frequency: %s' % description['frequency'])
    storm.log('max-count: %s' % str(description['max-count']))
    storm.log('group:     %s' % str(description['group']))

    net = Mininet_wifi(controller=Controller, accessPoint=OVSKernelAP)

    storm.log('Setting up the controller')
    c1 = net.addController('c1', controller=Controller)
    c1.start()

    # Setting the network mode and channel according to the frequency specified
    if frequency == '2.4g':
        # Default channel 1 for 2.4GHz frequency (mode=802.11n)
        description['mode'] = 'n'
        description['channel'] = '1'
    elif frequency == '5g':
        # Default channel 36 for 5GHz frequency (mode=802.11ac)
        description['mode'] = 'ac'
        description['channel'] = '36'

    # Calculate the start index of each group
    group_start = []
    step = max_count / group
    i = 0
    while i < max_count:
        group_start.append(i)
        i += step
    storm.log('group_start: ' + str(group_start))

    # Add nodes in this topology
    for i in range(0, len(group_start)):
        station_name = 'sta' + str(i)
        ap_name = 'ap' + str(i)
        host_name = 'h' + str(i)

        station = net.addStation(station_name, range=100,
                                 position='%s, 10, 0' % str(i * 50 + 20))
        ap = net.addAccessPoint(
            ap_name, ssid=ap_name, mode=description['mode'],
            channel=description['channel'],
            position='%s, 20, 0' % str(i * 50 + 20), range=20)
        host = net.addHost(host_name)

    net.configureWifiNodes()

    # Add links between nodes
    for i in range(0, len(group_start)):
        station = net.get('sta' + str(i))
        ap = net.get('ap' + str(i))
        host = net.get('h' + str(i))
        net.addLink(station, ap)
        net.addLink(ap, host, rtt=0.1, loss=0.001, bw=1000)

    net.build()

    # Start the APs
    for i in range(0, len(group_start)):
        ap_name = 'ap' + str(i)
        ap = net.get(ap_name)
        ap.start([c1])

    # Run the test (see ./run.sh for details)
    for i in range(0, len(group_start)):
        sender_name = 'sta' + str(i)
        receiver_name = 'h' + str(i)
        sender = net.get(sender_name)
        receiver = net.get(receiver_name)
        # Disable TSO at both sender and receiver
        sender.cmd('ethtool -K ' + sender_name + '-wlan0 tso off')
        receiver.cmd('ethtool -K ' + receiver_name + '-eth0 tso off')

        # Start the iperf3 deamon at receiver
        receiver.cmd('iperf3 -s -D -A %s' % str(i))
        storm.log('iperf3 -s -D -A %s' % str(i))

        storm.log('Run the test 3s later: %s-%s' %
                  (str(group_start[i]), str(group_start[i] + step - 1)))
        time.sleep(3)

        # Launch the test
        shell_command = shell_command_template % (
            algorithm, receiver.IP(), frequency,
            str(group_start[i]), str(group_start[i] + step),
            'runtime-' + algorithm + '-' + frequency + '-' + str(i) + '.log'
        )
        storm.log(shell_command)
        sender.cmd(shell_command)

    # Start the CLI to provide controllability on this network
    CLI_wifi(net)

    net.stop()


if __name__ == "__main__":
    main(sys.argv[1:])
