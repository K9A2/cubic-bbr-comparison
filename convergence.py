#!/usr/bin/python
# coding=utf-8

import sys
import getopt
import json

import numpy as np

import libstorm as storm


rtt = [30, 100, 200]
loss = [0.01, 0.10, 1.0]

task_description = {
    'algorithm': '',
    'max_count': 0,
    'window': 0
}

iperf_file_name_template = \
    './convergence-%s/iperf3-%s-rtt%s-loss%s-600s-%s.json'


def usage():
    print 'Use this script to get the <convergence time>, <stability> and'
    print '<average congestion window> from all JSON files obtained via iperf3'
    print ''
    print 'Usage convergence.py [-a|--algorithm <algorithm>]'
    print '      convergence.py [-m|--max-count <count>]'
    print '      convergence.py [-w|--window <window>]'
    print '      convergence.py [-h|--help]'
    print ''
    print 'You need to specify both <algorithm>, <count> and <window> in'
    print 'command line'


def parse_options(argv):
    try:
        opts, args = \
            getopt.getopt(argv, 'ha:m:w:',
                          ['help', 'algorithm=', 'max-count=', 'window='])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        if opt in ('-a', '--algorithm'):
            task_description['algorithm'] = arg
        if opt in ('-m', '--max-count'):
            task_description['max_count'] = int(arg)
        if opt in ('-w', '--window'):
            task_description['window'] = int(arg)


def main(argv):

    parse_options(argv)

    print 'algorithm: ' + task_description['algorithm']
    print 'max_count: ' + str(task_description['max_count'])
    print 'window: ' + str(task_description['window'])

    for r in rtt:
        for l in loss:
            # Time to reach convergence
            convergence_time = []
            # Stability after convergence. Measured with the standard
            # devidation of smaples after convergence to the end of test
            stability = []
            # The average congestion window in this test
            average_cwnd = []
            for i in range(0, task_description['max_count']):
                algorithm = task_description['algorithm']
                window = task_description['window']
                file_name = iperf_file_name_template % \
                    (algorithm, algorithm, str(r), str(l), str(i))
                json_object = json.load(open(file_name, 'r'))
                intervals = json_object['intervals']
                cwnd = storm.get_field_array(intervals, 'snd_cwnd', storm.K)

                # Calculate the average congestion window
                avg_cwnd = np.average(cwnd)
                average_cwnd.append(avg_cwnd)

                # Calculate the moving average of congestion window with given
                # window
                ma_cwnd = storm.getMovingAverage(cwnd, window)

                # Calculate the time of convergence
                tc = storm.getFirst(ma_cwnd, avg_cwnd * 1.2, avg_cwnd * 0.8)
                convergence_time.append(tc)

                # Calculate the stability of convergence
                s = np.std(ma_cwnd)
                stability.append(s)

            print '----------------------------------------'
            print 'rtt%s-loss%s:' % (str(r), str(l))
            print 'average cwnd:     %.2f' % np.average(average_cwnd)
            print 'convergence time: %.2f' % np.average(convergence_time)
            print 'stability:        %.2f' % np.average(stability)
            print 'stability in %%    %.2f' % \
                np.average(stability / np.average(average_cwnd) * 100)


if __name__ == '__main__':
    main(sys.argv[1:])
