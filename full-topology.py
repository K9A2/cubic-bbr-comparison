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


loss = [0.01, 0.05, 0.10, 0.20, 0.40, 0.60, 0.80, 1.00, 3.00, 5.00]
rtt = [12, 30, 60, 100, 200, 300]
# rtt = [12, 30, 60]

algorithm = 'illinois'
tcpdump_command_template = \
    'tcpdump -i %s-eth0 tcp 1> ./tcpdump-%s-rtt%s-loss%s-1g-%s.log &'
shell_command_template = './run.sh -c %s -a %s -r %s -l %s 1> %s &'


class FullTopology(Topo):

    def __init__(self):
        Topo.__init__(self)

        i = 0
        # 按照设定的 RTT 和丢包率来依次建立拓扑
        for r in rtt:
            for l in loss:
                # 主机和交换机名称
                sender_name = 'h' + str(i)
                receiver_name = 'h' + str(i + 1)

                sender_switch_name = 's' + str(i)
                receiver_switch_name = 's' + str(i + 1)

                i += 2

                # 添加收发双方主机和路由器
                sender = self.addHost(sender_name)
                sender_switch = self.addSwitch(sender_switch_name)
                receiver = self.addHost(receiver_name)
                receiver_switch = self.addSwitch(receiver_switch_name)

                # 连接各主机和路由器
                self.addLink(sender, sender_switch,
                             bw=1000, delay=str(r / 6) + 'ms', loss=0)
                self.addLink(sender_switch, receiver_switch,
                             bw=100, delay=str(r / 6) + 'ms', loss=l)
                self.addLink(receiver_switch, receiver,
                             bw=1000, delay=str(r / 6) + 'ms', loss=0)


def run():

    net = Mininet(topo=FullTopology(), host=CPULimitedHost, link=TCLink)
    net.start()

    # 在运行前设置各主机
    i = 0
    for r in rtt:
        for l in loss:
            sender_name = 'h' + str(i)
            receiver_name = 'h' + str(i + 1)
            i += 2

            sender = net.get(sender_name)
            receiver = net.get(receiver_name)

            # 关闭所有主机的 tso 功能
            sender.cmd('ethtool -K ' + sender_name + '-eth0 tso off')
            receiver.cmd('ethtool -K ' + receiver_name + '-eth0 tso off')

            time.sleep(3)

            # 在接收方开启 iperf daemon
            receiver.cmd('iperf3 -s -D')

            # 在收发双方进行 tcpdump 抓包
            sender.cmd(tcpdump_command_template % (
                sender_name, algorithm, str(r), str(l), 'sender'))
            receiver.cmd(tcpdump_command_template % (
                receiver_name, algorithm, str(r), str(l), 'receiver'))

            storm.log('sleep 3s to run the test')
            time.sleep(3)

            # run the test
            sender.cmd(shell_command_template % (
                algorithm, receiver.IP(), str(r), str(l),
                'runtime-rtt' + str(r) + '-loss' + str(l) + '.log'
            ))

            storm.log('rtt' + str(r) + '-loss' + str(l) + ' started')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    # clear potential dangling network NICs before setting up the new network
    os.system('mn -c')
    setLogLevel('info')
    run()
