#!/usr/bing/python
# coding=utf-8


import os
import signal

import psutil as ps


def main():

    # Get pids for all processes, and kill those iperf or iperf3 processes
    pids = ps.pids()
    for pid in pids:
        p = ps.Process(pid)
        if p.name() == 'iperf' or p.name() == 'iperf3':
            print('pid: %s, name: %s, to be killed' % (pid, p.name()))
            os.kill(pid, signal.SIGKILL)


if __name__ == '__main__':
    main()
