#!/usr/bin/python
# coding=utf-8

import os
import sys
import getopt


loss = [0.01, 0.10, 1.0]
rtt = [30, 100, 200]

iperf_file_name_template = \
    './convergence-%s/iperf3-%s-rtt%s-loss%s-600s-%s.json'


def usage():
    print 'Usage: file-validate.py [-a|--algorithm <algorithm>]'
    print '       file-validate.py [-m|--max-count <count>]'
    print '       file-validate.py [-h|--help]'
    print 'You need to specify both <algorithm> and <count> in command line'


def main(argv):

    algorithm = ''
    max_count = 0

    try:
        opts, args = getopt.getopt(argv, 'ha:m:',
                                   ['help', 'algorithm=', 'max-count='])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        if opt in ('-a', '--algorithm'):
            algorithm = arg
        if opt in ('-m', '--max-count'):
            max_count = int(arg)

    missed_file = 0
    for r in rtt:
        for l in loss:
            for i in range(0, max_count):
                file_name = iperf_file_name_template % \
                    (algorithm, algorithm, str(r), str(l), str(i))
                if not os.path.isfile(file_name):
                    print file_name + ' not exists!'
                    missed_file += 1

    if missed_file == 0:
        print 'No file missed'


if __name__ == '__main__':
    main(sys.argv[1:])
