#!/usr/bin/python
# coding=utf-8

import argparse
import json
import sys

import numpy as np

import libstorm as storm

# Default RTT and loss rate for wired scenarios
rtt = [30, 100, 200]
loss = [0.01, 0.10, 1.0]

# File name of iperf3 JSON file for wired and wireless scenarios
wired_file = 'iperf3-%s-rtt%s-loss%s-600s-%s.json'
wireless_file = 'iperf3-%s-frequency%s-600s-%s.json'

dir_template = './convergence-%s/'

# Use this dict to store the arguments from command line
description = {}


def parse_options():
  parser = argparse.ArgumentParser(
      description='Use this script to get the <CONVERGENCE TIME>, <STABILITY> \
      and <AVERAGE CONGESTION WINDOW> from all JSON files obtained via iperf3.',
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument(
      '-a', default='cubic', action='store', dest='algorithm', type=str,
      help='the congestion control protocol needed to ba analyzed')
  parser.add_argument(
      '-m', default=120, action='store', dest='max', type=int,
      help='the maximum number of JSON files')
  parser.add_argument(
      '-w', default=30, action='store', dest='window', type=int,
      help='the window size used to calculate the moving average')
  parser.add_argument(
      '-s', default='wired', action='store', dest='scenario', type=str,
      help='the target scenario, can be wired/2.4g/5g')

  args = parser.parse_args()

  description['algorithm'] = args.algorithm
  description['max_count'] = args.max
  description['window'] = args.window
  description['scenario'] = args.scenario


def get_stat(file_name):
  json_object = json.load(open(file_name, 'r'))
  intervals = json_object['intervals']
  cwnd = storm.get_field_array(intervals, 'snd_cwnd', storm.K)

  # Calculate the average congestion window
  avg_cwnd = np.average(cwnd)
  # Calculate the moving average of congestion window with given window
  ma_cwnd = storm.getMovingAverage(cwnd, description['window'])
  # Calculate the time of convergence
  tc = storm.getFirst(ma_cwnd, avg_cwnd * 1.2, avg_cwnd * 0.8)
  # Calculate the stability of convergence
  s = np.std(ma_cwnd)

  return avg_cwnd, tc, s


def print_stats(average_cwnd, convergence_time, stability):
  print 'average cwnd:     %.2f' % np.average(average_cwnd)
  print 'convergence time: %.2f' % np.average(convergence_time)
  print 'stability:        %.2f' % np.average(stability)
  print 'stability in %%    %.2f' % \
      np.average(stability / np.average(average_cwnd) * 100)


def main():

  parse_options()

  algorithm = description['algorithm']
  max_count = description['max_count']
  window = description['window']
  scenario = description['scenario']

  storm.log('Received arguments:')
  storm.log('algorithm: ' + algorithm)
  storm.log('max_count: ' + str(max_count))
  storm.log('window:    ' + str(window))
  storm.log('scenario:  ' + scenario)

  if scenario == 'wired':
    for r in rtt:
      for l in loss:
        # Time to reach convergence
        convergence_time = []
        # Stability after convergence. Measured with the standard
        # devidation of samples after convergence to the end of test
        stability = []
        # The average congestion window in this test
        average_cwnd = []

        for i in range(0, max_count):
          working_dir = (dir_template % algorithm) + scenario + '/'
          file_name = working_dir + \
              (wired_file % (algorithm, str(r), str(l), str(i)))
          avg_cwnd, tc, s = get_stat(file_name)
          average_cwnd.append(avg_cwnd)
          convergence_time.append(tc)
          stability.append(s)

        print '----------------------------------------'
        print 'rtt%s-loss%s:' % (str(r), str(l))
        print_stats(average_cwnd, convergence_time, stability)

  elif scenario == '2.4g' or scenario == '5g':
    convergence_time = []
    stability = []
    average_cwnd = []

    for i in range(0, max_count):
      working_dir = (dir_template % algorithm) + scenario + '/'
      file_name = working_dir + (wireless_file % (algorithm, scenario, str(i)))

      avg_cwnd, tc, s = get_stat(file_name)
      average_cwnd.append(avg_cwnd)
      convergence_time.append(tc)
      stability.append(s)

    print '----------------------------------------'
    print '%s:' % scenario
    print_stats(average_cwnd, convergence_time, stability)


if __name__ == '__main__':
  main()
