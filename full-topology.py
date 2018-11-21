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

loss_rate = [0.05, 0.20, 0.40, 0.60, 0.80]

class FullTopology(Topo):

  def __init__(self):
    Topo.__init__(self)

    # -------- rtt = 12ms --------

    h1 = self.addHost('h1')
    h2 = self.addHost('h2')
    s1 = self.addSwitch('s1')
    s2 = self.addSwitch('s2')
    # loss = 0.05%
    self.addLink(h1, s1, bw=1000, delay='2ms', loss=0)
    self.addLink(s1, s2, bw=100, delay='2ms', loss=loss_rate[0])
    self.addLink(s2, h2, bw=1000, delay='2ms', loss=0)

    h3 = self.addHost('h3')
    h4 = self.addHost('h4')
    s3 = self.addSwitch('s3')
    s4 = self.addSwitch('s4')
    # loss = 0.20%
    self.addLink(h3, s3, bw=1000, delay='2ms', loss=0)
    self.addLink(s3, s4, bw=100, delay='2ms', loss=loss_rate[1])
    self.addLink(s4, h4, bw=1000, delay='2ms', loss=0)

    h5 = self.addHost('h5')
    h6 = self.addHost('h6')
    s5 = self.addSwitch('s5')
    s6 = self.addSwitch('s6')
    # loss = 0.40%
    self.addLink(h5, s5, bw=1000, delay='2ms', loss=0)
    self.addLink(s5, s6, bw=100, delay='2ms', loss=loss_rate[2])
    self.addLink(s6, h6, bw=1000, delay='2ms', loss=0)

    h7 = self.addHost('h7')
    h8 = self.addHost('h8')
    s7 = self.addSwitch('s7')
    s8 = self.addSwitch('s8')
    # loss = 0.60%
    self.addLink(h7, s7, bw=1000, delay='2ms', loss=0)
    self.addLink(s7, s8, bw=100, delay='2ms', loss=loss_rate[3])
    self.addLink(s8, h8, bw=1000, delay='2ms', loss=0)

    h9 = self.addHost('h9')
    h10 = self.addHost('h10')
    s9 = self.addSwitch('s9')
    s10 = self.addSwitch('s10')
    # loss = 0.80%
    self.addLink(h9, s9, bw=1000, delay='2ms', loss=0)
    self.addLink(s9, s10, bw=100, delay='2ms', loss=loss_rate[4])
    self.addLink(s10, h10, bw=1000, delay='2ms', loss=0)

    # -------- rtt = 30ms --------

    h11 = self.addHost('h11')
    h12 = self.addHost('h12')
    s11 = self.addSwitch('s11')
    s12 = self.addSwitch('s12')
    # loss = 0.05%
    self.addLink(h11, s11, bw=1000, delay='5ms', loss=0)
    self.addLink(s11, s12, bw=100, delay='5ms', loss=loss_rate[0])
    self.addLink(s12, h12, bw=1000, delay='5ms', loss=0)

    h13 = self.addHost('h13')
    h14 = self.addHost('h14')
    s13 = self.addSwitch('s13')
    s14 = self.addSwitch('s14')
    # loss = 0.20%
    self.addLink(h13, s13, bw=1000, delay='5ms', loss=0)
    self.addLink(s13, s14, bw=100, delay='5ms', loss=loss_rate[1])
    self.addLink(s14, h14, bw=1000, delay='5ms', loss=0)

    h15 = self.addHost('h15')
    h16 = self.addHost('h16')
    s15 = self.addSwitch('s15')
    s16 = self.addSwitch('s16')
    # loss = 0.40%
    self.addLink(h15, s15, bw=1000, delay='5ms', loss=0)
    self.addLink(s15, s16, bw=100, delay='5ms', loss=loss_rate[2])
    self.addLink(s16, h16, bw=1000, delay='5ms', loss=0)

    h17 = self.addHost('h17')
    h18 = self.addHost('h18')
    s17 = self.addSwitch('s17')
    s18 = self.addSwitch('s18')
    # loss = 0.60%
    self.addLink(h17, s17, bw=1000, delay='5ms', loss=0)
    self.addLink(s17, s18, bw=100, delay='5ms', loss=loss_rate[3])
    self.addLink(s18, h18, bw=1000, delay='5ms', loss=0)

    h19 = self.addHost('h19')
    h20 = self.addHost('h20')
    s19 = self.addSwitch('s19')
    s20 = self.addSwitch('s20')
    # loss = 0.80%
    self.addLink(h19, s19, bw=1000, delay='5ms', loss=0)
    self.addLink(s19, s20, bw=100, delay='5ms', loss=loss_rate[4])
    self.addLink(s20, h20, bw=1000, delay='5ms', loss=0)

    # -------- rtt = 60ms --------

    h21 = self.addHost('h21')
    h22 = self.addHost('h22')
    s21 = self.addSwitch('s21')
    s22 = self.addSwitch('s22')
    # loss = 0.05%
    self.addLink(h21, s21, bw=1000, delay='10ms', loss=0)
    self.addLink(s21, s22, bw=100, delay='10ms', loss=loss_rate[0])
    self.addLink(s22, h22, bw=1000, delay='10ms', loss=0)

    h23 = self.addHost('h23')
    h24 = self.addHost('h24')
    s23 = self.addSwitch('s23')
    s24 = self.addSwitch('s24')
    # loss = 0.2%
    self.addLink(h23, s23, bw=1000, delay='10ms', loss=0)
    self.addLink(s23, s24, bw=100, delay='10ms', loss=loss_rate[1])
    self.addLink(s24, h24, bw=1000, delay='10ms', loss=0)

    h25 = self.addHost('h25')
    h26 = self.addHost('h26')
    s25 = self.addSwitch('s25')
    s26 = self.addSwitch('s26')
    # loss = 0.4%
    self.addLink(h25, s25, bw=1000, delay='10ms', loss=0)
    self.addLink(s25, s26, bw=100, delay='10ms', loss=loss_rate[2])
    self.addLink(s26, h26, bw=1000, delay='10ms', loss=0)

    h27 = self.addHost('h27')
    h28 = self.addHost('h28')
    s27 = self.addSwitch('s27')
    s28 = self.addSwitch('s28')
    # loss = 0.6%
    self.addLink(h27, s27, bw=1000, delay='10ms', loss=0)
    self.addLink(s27, s28, bw=100, delay='10ms', loss=loss_rate[3])
    self.addLink(s28, h28, bw=1000, delay='10ms', loss=0)

    h29 = self.addHost('h29')
    h30 = self.addHost('h30')
    s29 = self.addSwitch('s29')
    s30 = self.addSwitch('s30')
    # loss = 0.8%
    self.addLink(h29, s29, bw=1000, delay='10ms', loss=0)
    self.addLink(s29, s30, bw=100, delay='10ms', loss=loss_rate[4])
    self.addLink(s30, h30, bw=1000, delay='10ms', loss=0)

    # -------- rtt = 100ms --------

    h31 = self.addHost('h31')
    h32 = self.addHost('h32')
    s31 = self.addSwitch('s31')
    s32 = self.addSwitch('s32')
    # loss = 0.05%
    self.addLink(h31, s31, bw=1000, delay='16ms', loss=0)
    self.addLink(s31, s32, bw=100, delay='16ms', loss=loss_rate[0])
    self.addLink(s32, h32, bw=1000, delay='16ms', loss=0)

    h33 = self.addHost('h33')
    h34 = self.addHost('h34')
    s33 = self.addSwitch('s33')
    s34 = self.addSwitch('s34')
    # loss = 0.20%
    self.addLink(h33, s33, bw=1000, delay='16ms', loss=0)
    self.addLink(s33, s34, bw=100, delay='16ms', loss=loss_rate[1])
    self.addLink(s34, h34, bw=1000, delay='16ms', loss=0)

    h35 = self.addHost('h35')
    h36 = self.addHost('h36')
    s35 = self.addSwitch('s35')
    s36 = self.addSwitch('s36')
    # loss = 0.40%
    self.addLink(h35, s35, bw=1000, delay='16ms', loss=0)
    self.addLink(s35, s36, bw=100, delay='16ms', loss=loss_rate[2])
    self.addLink(s36, h36, bw=1000, delay='16ms', loss=0)

    h37 = self.addHost('h37')
    h38 = self.addHost('h38')
    s37 = self.addSwitch('s37')
    s38 = self.addSwitch('s38')
    # loss = 0.60%
    self.addLink(h37, s37, bw=1000, delay='16ms', loss=0)
    self.addLink(s37, s38, bw=100, delay='16ms', loss=loss_rate[3])
    self.addLink(s38, h38, bw=1000, delay='16ms', loss=0)

    h39 = self.addHost('h39')
    h40 = self.addHost('h40')
    s39 = self.addSwitch('s39')
    s40 = self.addSwitch('s40')
    # loss = 0.80%
    self.addLink(h39, s39, bw=1000, delay='16ms', loss=0)
    self.addLink(s39, s40, bw=100, delay='16ms', loss=loss_rate[4])
    self.addLink(s40, h40, bw=1000, delay='16ms', loss=0)

    # -------- rtt = 200ms --------

    h41 = self.addHost('h41')
    h42 = self.addHost('h42')
    s41 = self.addSwitch('s41')
    s42 = self.addSwitch('s42')
    # loss = 0.05%
    self.addLink(h41, s41, bw=1000, delay='33ms', loss=0)
    self.addLink(s41, s42, bw=100, delay='33ms', loss=loss_rate[0])
    self.addLink(s42, h42, bw=1000, delay='33ms', loss=0)

    h43 = self.addHost('h43')
    h44 = self.addHost('h44')
    s43 = self.addSwitch('s43')
    s44 = self.addSwitch('s44')
    # loss = 0.20%
    self.addLink(h43, s43, bw=1000, delay='33ms', loss=0)
    self.addLink(s43, s44, bw=100, delay='33ms', loss=loss_rate[1])
    self.addLink(s44, h44, bw=1000, delay='33ms', loss=0)

    h45 = self.addHost('h45')
    h46 = self.addHost('h46')
    s45 = self.addSwitch('s45')
    s46 = self.addSwitch('s46')
    # loss = 0.40%
    self.addLink(h45, s45, bw=1000, delay='33ms', loss=0)
    self.addLink(s45, s46, bw=100, delay='33ms', loss=loss_rate[2])
    self.addLink(s46, h46, bw=1000, delay='33ms', loss=0)

    h47 = self.addHost('h47')
    h48 = self.addHost('h48')
    s47 = self.addSwitch('s47')
    s48 = self.addSwitch('s48')
    # loss = 0.60%
    self.addLink(h47, s47, bw=1000, delay='33ms', loss=0)
    self.addLink(s47, s48, bw=100, delay='33ms', loss=loss_rate[3])
    self.addLink(s48, h48, bw=1000, delay='33ms', loss=0)

    h49 = self.addHost('h49')
    h50 = self.addHost('h50')
    s49 = self.addSwitch('s49')
    s50 = self.addSwitch('s50')
    # loss = 0.80%
    self.addLink(h49, s49, bw=1000, delay='33ms', loss=0)
    self.addLink(s49, s50, bw=100, delay='33ms', loss=loss_rate[4])
    self.addLink(s50, h50, bw=1000, delay='33ms', loss=0)

    # -------- rtt = 300ms --------

    h51 = self.addHost('h51')
    h52 = self.addHost('h52')
    s51 = self.addSwitch('s51')
    s52 = self.addSwitch('s52')
    # loss = 0.05%
    self.addLink(h51, s51, bw=1000, delay='50ms', loss=0)
    self.addLink(s51, s52, bw=100, delay='50ms', loss=loss_rate[0])
    self.addLink(s52, h52, bw=1000, delay='50ms', loss=0)

    h53 = self.addHost('h53')
    h54 = self.addHost('h54')
    s53 = self.addSwitch('s53')
    s54 = self.addSwitch('s54')
    # loss = 0.20%
    self.addLink(h53, s53, bw=1000, delay='50ms', loss=0)
    self.addLink(s53, s54, bw=100, delay='50ms', loss=loss_rate[1])
    self.addLink(s54, h54, bw=1000, delay='50ms', loss=0)

    h55 = self.addHost('h55')
    h56 = self.addHost('h56')
    s55 = self.addSwitch('s55')
    s56 = self.addSwitch('s56')
    # loss = 0.40%
    self.addLink(h55, s55, bw=1000, delay='50ms', loss=0)
    self.addLink(s55, h56, bw=100, delay='50ms', loss=loss_rate[2])
    self.addLink(s56, h56, bw=1000, delay='50ms', loss=0)

    h57 = self.addHost('h57')
    h58 = self.addHost('h58')
    s57 = self.addSwitch('s57')
    s58 = self.addSwitch('s58')
    # loss = 0.60%
    self.addLink(h57, s57, bw=1000, delay='50ms', loss=0)
    self.addLink(s57, s58, bw=100, delay='50ms', loss=loss_rate[3])
    self.addLink(s58, h58, bw=1000, delay='50ms', loss=0)

    h59 = self.addHost('h59')
    h60 = self.addHost('h60')
    s59 = self.addSwitch('s59')
    s60 = self.addSwitch('s60')
    # loss = 0.80%
    self.addLink(h59, s59, bw=1000, delay='50ms', loss=0)
    self.addLink(s59, s60, bw=100, delay='50ms', loss=loss_rate[4])
    self.addLink(s60, h60, bw=1000, delay='50ms', loss=0)


def run():

  net = Mininet(topo=FullTopology(), host=CPULimitedHost, link=TCLink)
  net.start()

  h1 = net.get('h1')
  h2 = net.get('h2')
  h1.cmd('ethtool -K h1-eth0 tso off')
  h2.cmd('ethtool -K h2-eth0 tso off')

  h3 = net.get('h3')
  h4 = net.get('h4')
  h3.cmd('ethtool -K h3-eth0 tso off')
  h4.cmd('ethtool -K h4-eth0 tso off')

  h5 = net.get('h5')
  h6 = net.get('h6')
  h5.cmd('ethtool -K h5-eth0 tso off')
  h6.cmd('ethtool -K h6-eth0 tso off')

  h7 = net.get('h7')
  h8 = net.get('h8')
  h7.cmd('ethtool -K h7-eth0 tso off')
  h8.cmd('ethtool -K h8-eth0 tso off')

  h9 = net.get('h9')
  h10 = net.get('h10')
  h9.cmd('ethtool -K h9-eth0 tso off')
  h10.cmd('ethtool -K h10-eth0 tso off')

  h11 = net.get('h11')
  h12 = net.get('h12')
  h11.cmd('ethtool -K h11-eth0 tso off')
  h12.cmd('ethtool -K h12-eth0 tso off')

  h13 = net.get('h13')
  h14 = net.get('h14')
  h13.cmd('ethtool -K h13-eth0 tso off')
  h14.cmd('ethtool -K h14-eth0 tso off')

  h15 = net.get('h15')
  h16 = net.get('h16')
  h15.cmd('ethtool -K h15-eth0 tso off')
  h16.cmd('ethtool -K h16-eth0 tso off')

  h17 = net.get('h17')
  h18 = net.get('h18')
  h17.cmd('ethtool -K h17-eth0 tso off')
  h18.cmd('ethtool -K h18-eth0 tso off')

  h19 = net.get('h19')
  h20 = net.get('h20')
  h19.cmd('ethtool -K h19-eth0 tso off')
  h20.cmd('ethtool -K h20-eth0 tso off')

  h21 = net.get('h21')
  h22 = net.get('h22')
  h21.cmd('ethtool -K h21-eth0 tso off')
  h22.cmd('ethtool -K h22-eth0 tso off')

  h23 = net.get('h23')
  h24 = net.get('h24')
  h23.cmd('ethtool -K h23-eth0 tso off')
  h24.cmd('ethtool -K h24-eth0 tso off')

  h25 = net.get('h25')
  h26 = net.get('h26')
  h25.cmd('ethtool -K h25-eth0 tso off')
  h26.cmd('ethtool -K h26-eth0 tso off')

  h27 = net.get('h27')
  h28 = net.get('h28')
  h27.cmd('ethtool -K h27-eth0 tso off')
  h28.cmd('ethtool -K h28-eth0 tso off')

  h29 = net.get('h29')
  h30 = net.get('h30')
  h29.cmd('ethtool -K h29-eth0 tso off')
  h30.cmd('ethtool -K h30-eth0 tso off')

  h31 = net.get('h31')
  h32 = net.get('h32')
  h31.cmd('ethtool -K h31-eth0 tso off')
  h32.cmd('ethtool -K h32-eth0 tso off')

  h33 = net.get('h33')
  h34 = net.get('h34')
  h33.cmd('ethtool -K h33-eth0 tso off')
  h34.cmd('ethtool -K h34-eth0 tso off')

  h35 = net.get('h35')
  h36 = net.get('h36')
  h35.cmd('ethtool -K h35-eth0 tso off')
  h36.cmd('ethtool -K h36-eth0 tso off')

  h37 = net.get('h37')
  h38 = net.get('h38')
  h37.cmd('ethtool -K h37-eth0 tso off')
  h38.cmd('ethtool -K h38-eth0 tso off')

  h39 = net.get('h39')
  h40 = net.get('h40')
  h39.cmd('ethtool -K h39-eth0 tso off')
  h40.cmd('ethtool -K h40-eth0 tso off')

  h41 = net.get('h41')
  h42 = net.get('h42')
  h41.cmd('ethtool -K h41-eth0 tso off')
  h42.cmd('ethtool -K h42-eth0 tso off')

  h43 = net.get('h43')
  h44 = net.get('h44')
  h43.cmd('ethtool -K h43-eth0 tso off')
  h44.cmd('ethtool -K h44-eth0 tso off')

  h45 = net.get('h45')
  h46 = net.get('h46')
  h45.cmd('ethtool -K h45-eth0 tso off')
  h46.cmd('ethtool -K h46-eth0 tso off')

  h47 = net.get('h47')
  h48 = net.get('h48')
  h47.cmd('ethtool -K h47-eth0 tso off')
  h48.cmd('ethtool -K h48-eth0 tso off')

  h49 = net.get('h49')
  h50 = net.get('h50')
  h49.cmd('ethtool -K h49-eth0 tso off')
  h50.cmd('ethtool -K h50-eth0 tso off')

  h51 = net.get('h51')
  h52 = net.get('h52')
  h51.cmd('ethtool -K h51-eth0 tso off')
  h52.cmd('ethtool -K h52-eth0 tso off')

  h53 = net.get('h53')
  h54 = net.get('h54')
  h53.cmd('ethtool -K h53-eth0 tso off')
  h54.cmd('ethtool -K h54-eth0 tso off')

  h55 = net.get('h55')
  h56 = net.get('h56')
  h55.cmd('ethtool -K h55-eth0 tso off')
  h56.cmd('ethtool -K h56-eth0 tso off')

  h57 = net.get('h57')
  h58 = net.get('h58')
  h57.cmd('ethtool -K h57-eth0 tso off')
  h58.cmd('ethtool -K h58-eth0 tso off')

  h59 = net.get('h59')
  h60 = net.get('h60')
  h59.cmd('ethtool -K h59-eth0 tso off')
  h60.cmd('ethtool -K h60-eth0 tso off')

  storm.log('Sleep 10 second to wait for the network fully setup')
  time.sleep(10)

  # ---- run the server as deamon ----

  h2.cmd('iperf3 -s -D')
  h4.cmd('iperf3 -s -D')
  h6.cmd('iperf3 -s -D')
  h8.cmd('iperf3 -s -D')
  h10.cmd('iperf3 -s -D')

  h12.cmd('iperf3 -s -D')
  h14.cmd('iperf3 -s -D')
  h16.cmd('iperf3 -s -D')
  h18.cmd('iperf3 -s -D')
  h20.cmd('iperf3 -s -D')

  h22.cmd('iperf3 -s -D')
  h24.cmd('iperf3 -s -D')
  h26.cmd('iperf3 -s -D')
  h28.cmd('iperf3 -s -D')
  h30.cmd('iperf3 -s -D')

  h32.cmd('iperf3 -s -D')
  h34.cmd('iperf3 -s -D')
  h36.cmd('iperf3 -s -D')
  h38.cmd('iperf3 -s -D')
  h40.cmd('iperf3 -s -D')

  h42.cmd('iperf3 -s -D')
  h44.cmd('iperf3 -s -D')
  h46.cmd('iperf3 -s -D')
  h48.cmd('iperf3 -s -D')
  h50.cmd('iperf3 -s -D')

  h52.cmd('iperf3 -s -D')
  h54.cmd('iperf3 -s -D')
  h56.cmd('iperf3 -s -D')
  h58.cmd('iperf3 -s -D')
  h60.cmd('iperf3 -s -D')

  storm.log('Deamons ready, wait 10 second to run the test')
  time.sleep(10)

  algorithm = 'cubic'
  tcpdump_command_template = 'tcpdump -i %s-eth0 tcp 1> ./tcpdump-%s-rtt%s-loss%s-1g-%s.log &'
  shell_command_template = './run.sh -c %s -a %s -r %s -l %s 1> %s &'

  # 12ms - start tcpdump
  h1.cmd(tcpdump_command_template % ('h1', algorithm, '12', loss_rate[0], 'sender'))
  h2.cmd(tcpdump_command_template % ('h2', algorithm, '12', loss_rate[0], 'receiver'))
  h3.cmd(tcpdump_command_template % ('h3', algorithm, '12', loss_rate[1], 'sender'))
  h4.cmd(tcpdump_command_template % ('h4', algorithm, '12', loss_rate[1], 'receiver'))
  h5.cmd(tcpdump_command_template % ('h5', algorithm, '12', loss_rate[2], 'sender'))
  h6.cmd(tcpdump_command_template % ('h6', algorithm, '12', loss_rate[2], 'receiver'))
  h7.cmd(tcpdump_command_template % ('h7', algorithm, '12', loss_rate[3], 'sender'))
  h8.cmd(tcpdump_command_template % ('h8', algorithm, '12', loss_rate[3], 'receiver'))
  h9.cmd(tcpdump_command_template % ('h9', algorithm, '12', loss_rate[4], 'sender'))
  h10.cmd(tcpdump_command_template % ('h10', algorithm, '12', loss_rate[4], 'receiver'))
  time.sleep(5)
  storm.log('rtt = 12ms dispatched')
  # 12ms - run the test
  h1.cmd(shell_command_template % (algorithm, '10.0.0.2', '12', loss_rate[0], 'runtime-rtt12-loss' + str(loss_rate[0]) + '.log'))
  h3.cmd(shell_command_template % (algorithm, '10.0.0.4', '12', loss_rate[1], 'runtime-rtt12-loss' + str(loss_rate[1]) + '.log'))
  h5.cmd(shell_command_template % (algorithm, '10.0.0.6', '12', loss_rate[2], 'runtime-rtt12-loss' + str(loss_rate[2]) + '.log'))
  h7.cmd(shell_command_template % (algorithm, '10.0.0.8', '12', loss_rate[3], 'runtime-rtt12-loss' + str(loss_rate[3]) + '.log'))
  h9.cmd(shell_command_template % (algorithm, '10.0.0.10', '12', loss_rate[4], 'runtime-rtt12-loss' + str(loss_rate[4]) +'.log'))

  # 30ms - start tcpdump
  h11.cmd(tcpdump_command_template % ('h11', algorithm, '30', loss_rate[0], 'sender'))
  h12.cmd(tcpdump_command_template % ('h12', algorithm, '30', loss_rate[0], 'receiver'))
  h13.cmd(tcpdump_command_template % ('h13', algorithm, '30', loss_rate[1], 'sender'))
  h14.cmd(tcpdump_command_template % ('h14', algorithm, '30', loss_rate[1], 'receiver'))
  h15.cmd(tcpdump_command_template % ('h15', algorithm, '30', loss_rate[2], 'sender'))
  h16.cmd(tcpdump_command_template % ('h16', algorithm, '30', loss_rate[2], 'receiver'))
  h17.cmd(tcpdump_command_template % ('h17', algorithm, '30', loss_rate[3], 'sender'))
  h18.cmd(tcpdump_command_template % ('h18', algorithm, '30', loss_rate[3], 'receiver'))
  h19.cmd(tcpdump_command_template % ('h19', algorithm, '30', loss_rate[4], 'sender'))
  h20.cmd(tcpdump_command_template % ('h20', algorithm, '30', loss_rate[4], 'receiver'))
  time.sleep(5)
  storm.log('rtt = 30ms dispatched')
  # 30ms - run the test
  h11.cmd(shell_command_template % (algorithm, '10.0.0.12', '30', loss_rate[0], 'runtime-rtt30-loss' + str(loss_rate[0]) + '.log'))
  h13.cmd(shell_command_template % (algorithm, '10.0.0.14', '30', loss_rate[1], 'runtime-rtt30-loss' + str(loss_rate[1]) + '.log'))
  h15.cmd(shell_command_template % (algorithm, '10.0.0.16', '30', loss_rate[2], 'runtime-rtt30-loss' + str(loss_rate[2]) + '.log'))
  h17.cmd(shell_command_template % (algorithm, '10.0.0.18', '30', loss_rate[3], 'runtime-rtt30-loss' + str(loss_rate[3]) + '.log'))
  h19.cmd(shell_command_template % (algorithm, '10.0.0.20', '30', loss_rate[4], 'runtime-rtt30-loss' + str(loss_rate[4]) + '.log'))

  # 60ms - start tcpdump
  h21.cmd(tcpdump_command_template % ('h21', algorithm, '60', loss_rate[0], 'sender'))
  h22.cmd(tcpdump_command_template % ('h22', algorithm, '60', loss_rate[0], 'receiver'))
  h23.cmd(tcpdump_command_template % ('h23', algorithm, '60', loss_rate[1], 'sender'))
  h24.cmd(tcpdump_command_template % ('h24', algorithm, '60', loss_rate[1], 'receiver'))
  h25.cmd(tcpdump_command_template % ('h25', algorithm, '60', loss_rate[2], 'sender'))
  h26.cmd(tcpdump_command_template % ('h26', algorithm, '60', loss_rate[2], 'receiver'))
  h27.cmd(tcpdump_command_template % ('h27', algorithm, '60', loss_rate[3], 'sender'))
  h28.cmd(tcpdump_command_template % ('h28', algorithm, '60', loss_rate[3], 'receiver'))
  h29.cmd(tcpdump_command_template % ('h29', algorithm, '60', loss_rate[4], 'sender'))
  h30.cmd(tcpdump_command_template % ('h30', algorithm, '60', loss_rate[4], 'receiver'))
  time.sleep(5)
  storm.log('rtt = 60ms dispatched')
  # 60ms - run the test
  h21.cmd(shell_command_template % (algorithm, '10.0.0.22', '60', loss_rate[0], 'runtime-rtt60-loss' + str(loss_rate[0]) + '.log'))
  h23.cmd(shell_command_template % (algorithm, '10.0.0.24', '60', loss_rate[1], 'runtime-rtt60-loss' + str(loss_rate[1]) + '.log'))
  h25.cmd(shell_command_template % (algorithm, '10.0.0.26', '60', loss_rate[2], 'runtime-rtt60-loss' + str(loss_rate[2]) + '.log'))
  h27.cmd(shell_command_template % (algorithm, '10.0.0.28', '60', loss_rate[3], 'runtime-rtt60-loss' + str(loss_rate[3]) + '.log'))
  h29.cmd(shell_command_template % (algorithm, '10.0.0.30', '60', loss_rate[4], 'runtime-rtt60-loss' + str(loss_rate[4]) + '.log'))

  # 100ms - start tcpdump
  h31.cmd(tcpdump_command_template % ('h31', algorithm, '100', loss_rate[0], 'sender'))
  h32.cmd(tcpdump_command_template % ('h32', algorithm, '100', loss_rate[0], 'receiver'))
  h33.cmd(tcpdump_command_template % ('h33', algorithm, '100', loss_rate[1], 'sender'))
  h34.cmd(tcpdump_command_template % ('h34', algorithm, '100', loss_rate[1], 'receiver'))
  h35.cmd(tcpdump_command_template % ('h35', algorithm, '100', loss_rate[2], 'sender'))
  h36.cmd(tcpdump_command_template % ('h36', algorithm, '100', loss_rate[2], 'receiver'))
  h37.cmd(tcpdump_command_template % ('h37', algorithm, '100', loss_rate[3], 'sender'))
  h38.cmd(tcpdump_command_template % ('h38', algorithm, '100', loss_rate[3], 'receiver'))
  h39.cmd(tcpdump_command_template % ('h39', algorithm, '100', loss_rate[4], 'sender'))
  h40.cmd(tcpdump_command_template % ('h40', algorithm, '100', loss_rate[4], 'receiver'))
  time.sleep(5)
  storm.log('rtt = 100ms dispatched')
  # 100ms - run the test
  h31.cmd(shell_command_template % (algorithm, '10.0.0.32', '100', loss_rate[0], 'runtime-rtt100-loss' + str(loss_rate[0]) + '.log'))
  h33.cmd(shell_command_template % (algorithm, '10.0.0.34', '100', loss_rate[1], 'runtime-rtt100-loss' + str(loss_rate[1]) + '.log'))
  h35.cmd(shell_command_template % (algorithm, '10.0.0.36', '100', loss_rate[2], 'runtime-rtt100-loss' + str(loss_rate[2]) + '.log'))
  h37.cmd(shell_command_template % (algorithm, '10.0.0.38', '100', loss_rate[3], 'runtime-rtt100-loss' + str(loss_rate[3]) + '.log'))
  h39.cmd(shell_command_template % (algorithm, '10.0.0.40', '100', loss_rate[4], 'runtime-rtt100-loss' + str(loss_rate[4]) + '.log'))

  # 200ms - start tcpdump
  h41.cmd(tcpdump_command_template % ('h41', algorithm, '200', loss_rate[0], 'sender'))
  h42.cmd(tcpdump_command_template % ('h42', algorithm, '200', loss_rate[0], 'receiver'))
  h43.cmd(tcpdump_command_template % ('h43', algorithm, '200', loss_rate[1], 'sender'))
  h44.cmd(tcpdump_command_template % ('h44', algorithm, '200', loss_rate[1], 'receiver'))
  h45.cmd(tcpdump_command_template % ('h45', algorithm, '200', loss_rate[2], 'sender'))
  h46.cmd(tcpdump_command_template % ('h46', algorithm, '200', loss_rate[2], 'receiver'))
  h47.cmd(tcpdump_command_template % ('h47', algorithm, '200', loss_rate[3], 'sender'))
  h48.cmd(tcpdump_command_template % ('h48', algorithm, '200', loss_rate[3], 'receiver'))
  h49.cmd(tcpdump_command_template % ('h49', algorithm, '200', loss_rate[4], 'sender'))
  h50.cmd(tcpdump_command_template % ('h50', algorithm, '200', loss_rate[4], 'receiver'))
  time.sleep(5)
  storm.log('rtt = 200ms dispatched')
  # 200ms - run the test
  h41.cmd(shell_command_template % (algorithm, '10.0.0.42', '200', loss_rate[0], 'runtime-rtt200-loss' + str(loss_rate[0]) + '.log'))
  h43.cmd(shell_command_template % (algorithm, '10.0.0.44', '200', loss_rate[1], 'runtime-rtt200-loss' + str(loss_rate[1]) + '.log'))
  h45.cmd(shell_command_template % (algorithm, '10.0.0.46', '200', loss_rate[2], 'runtime-rtt200-loss' + str(loss_rate[2]) + '.log'))
  h47.cmd(shell_command_template % (algorithm, '10.0.0.48', '200', loss_rate[3], 'runtime-rtt200-loss' + str(loss_rate[3]) + '.log'))
  h49.cmd(shell_command_template % (algorithm, '10.0.0.50', '200', loss_rate[4], 'runtime-rtt200-loss' + str(loss_rate[4]) + '.log'))

  # 300ms - start tcpdump
  h51.cmd(tcpdump_command_template % ('h51', algorithm, '300', loss_rate[0], 'sender'))
  h52.cmd(tcpdump_command_template % ('h52', algorithm, '300', loss_rate[0], 'receiver'))
  h53.cmd(tcpdump_command_template % ('h53', algorithm, '300', loss_rate[1], 'sender'))
  h54.cmd(tcpdump_command_template % ('h54', algorithm, '300', loss_rate[1], 'receiver'))
  h55.cmd(tcpdump_command_template % ('h55', algorithm, '300', loss_rate[2], 'sender'))
  h56.cmd(tcpdump_command_template % ('h56', algorithm, '300', loss_rate[2], 'receiver'))
  h57.cmd(tcpdump_command_template % ('h57', algorithm, '300', loss_rate[3], 'sender'))
  h58.cmd(tcpdump_command_template % ('h58', algorithm, '300', loss_rate[3], 'receiver'))
  h59.cmd(tcpdump_command_template % ('h59', algorithm, '300', loss_rate[4], 'sender'))
  h60.cmd(tcpdump_command_template % ('h60', algorithm, '300', loss_rate[4], 'receiver'))
  time.sleep(5)
  storm.log('rtt = 300ms dispatched')
  # 300ms - run the test
  h51.cmd(shell_command_template % (algorithm, '10.0.0.52', '300', loss_rate[0], 'runtime-rtt300-loss' + str(loss_rate[0]) + '.log'))
  h53.cmd(shell_command_template % (algorithm, '10.0.0.54', '300', loss_rate[1], 'runtime-rtt300-loss' + str(loss_rate[1]) + '.log'))
  h55.cmd(shell_command_template % (algorithm, '10.0.0.56', '300', loss_rate[2], 'runtime-rtt300-loss' + str(loss_rate[2]) + '.log'))
  h57.cmd(shell_command_template % (algorithm, '10.0.0.58', '300', loss_rate[3], 'runtime-rtt300-loss' + str(loss_rate[3]) + '.log'))
  h59.cmd(shell_command_template % (algorithm, '10.0.0.60', '300', loss_rate[4], 'runtime-rtt300-loss' + str(loss_rate[4]) + '.log'))

  storm.log('test start in background')

  CLI(net)
  net.stop()


if __name__ == '__main__':
  # clear potential dangling network NICs before setting up the new network
  os.system('mn -c')
  setLogLevel('info')
  run()
