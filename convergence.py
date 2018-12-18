#!/usr/bin/python
# coding=utf-8

import argparse
import json
import sys

import matplotlib.pyplot as plt
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

# All evaluated scenarios
scenario = ['wired', '2.4g', '5g']

# Use designated colors to avoid repetition
line_color = [
    'darkorange', 'slateblue', 'yellowgreen', 'red', 'black',
    'firebrick', 'gold', 'seagreen', 'chartreuse', 'deepskyblue',
    'darkorchid'
]


def parse_options():
  parser = argparse.ArgumentParser(
      description='Use this script to get the <CONVERGENCE TIME>, <STABILITY> \
      and <AVERAGE CONGESTION WINDOW> from all JSON files obtained via iperf3.',
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  # Functional arguments
  parser.add_argument(
      '-a', '--algorithm', default='cubic', action='store', dest='algorithm',
      type=str, metavar='',
      help='the congestion control protocol needed to ba analyzed')
  parser.add_argument(
      '-m', '--max', default=120, action='store', dest='max', type=int,
      metavar='', help='the maximum number of JSON files')
  parser.add_argument(
      '-w', '--window', default=30, action='store', dest='window', type=int,
      metavar='', help='the window size used to calculate the moving average')

  # Output as CDF is optional
  parser.add_argument(
      '-f', '--figure', default=False, action='store_true', dest='figure_output',
      help='the results will output as CDF figure')

  # Draw a separate legend is an optional feature
  parser.add_argument(
      '-l', '--legend', default=False, action='store_true', dest='legend',
      help='provide a separate legend in a separate figure')

  args = parser.parse_args()

  description['algorithm'] = args.algorithm
  description['max_count'] = args.max
  description['window'] = args.window

  description['figure_output'] = args.figure_output
  description['legend'] = args.legend


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

  # Calculate the throughput of this evaluation
  throughput = storm.get_field_array(intervals, 'bits_per_second', storm.M)

  return {
      'avg_cwnd': avg_cwnd,
      'tc': tc,
      's': s,
      'throughput': np.average(throughput)
  }


def get_result_set():
  return {
      # Time to reach convergence
      'convergence_time': [],
      # Stability after convergence. Measured with the standard devidation
      # of samples after convergence to the end of test
      'stability': [],
      # The average congestion window in this test
      'average_cwnd': [],
      # The throughput measured by iperf3
      'throughput': []
  }


def get_cdf_axises(values):
  cdf_x = np.sort(values)
  cdf_y = []
  length = len(cdf_x)
  for i in range(0, length):
    cdf_y.append(float(i) / float(length))
  return cdf_x, cdf_y


def print_stats(average_cwnd, convergence_time, stability, throughput):
  print 'average cwnd:     %.2f' % np.average(average_cwnd)
  print 'convergence time: %.2f' % np.average(convergence_time)
  print 'stability:        %.2f' % np.average(stability)
  print 'stability in %%:   %.2f' \
      % np.average(stability / np.average(average_cwnd) * 100)
  print 'throughput:       %.2f' % np.average(throughput)


def main():

  parse_options()

  algorithm = description['algorithm']
  max_count = description['max_count']
  window = description['window']

  figure_output = description['figure_output']
  legend_out = description['legend']

  storm.log('Received arguments:')
  storm.log('algorithm: ' + algorithm)
  storm.log('max_count: ' + str(max_count))
  storm.log('window:    ' + str(window))

  storm.log('output as CDF figure: ' + str(figure_output))
  storm.log('draw a separate legend: ' + str(legend_out))

  if figure_output == True:
    global_stats = {}

  # Load results for wired scenarios
  for r in rtt:
    for l in loss:
      key = 'RTT %sms, loss %s %%' % (r, l)
      result_set = get_result_set()
      # Read results
      for i in range(0, max_count):
        working_dir = (dir_template % algorithm) + scenario[0] + '/'
        file_name = working_dir \
            + (wired_file % (algorithm, str(r), str(l), str(i)))
        stat = get_stat(file_name)
        result_set['average_cwnd'].append(stat['avg_cwnd'])
        result_set['convergence_time'].append(stat['tc'])
        result_set['stability'].append(stat['s'])
        result_set['throughput'].append(stat['throughput'])
      # Calculate the CDF axises
      cdf_x, cdf_y = get_cdf_axises(result_set['convergence_time'])
      result_set['cdf_x'] = cdf_x
      result_set['cdf_y'] = cdf_y

      if figure_output == True:
        global_stats[key] = result_set

      # Print local results
      print '----------------------------------------'
      print 'rtt%s-loss%s:' % (str(r), str(l))
      print_stats(result_set['average_cwnd'], result_set['convergence_time'],
                  result_set['stability'], result_set['throughput'])

  # Load results for wireless scenarios
  for i in range(1, len(scenario)):
    key = scenario[i]
    result_set = get_result_set()
    for j in range(0, max_count):
      working_dir = (dir_template % algorithm) + scenario[i] + '/'
      file_name = working_dir \
          + (wireless_file % (algorithm, scenario[i], str(j)))

      stat = get_stat(file_name)
      result_set['average_cwnd'].append(stat['avg_cwnd'])
      result_set['convergence_time'].append(stat['tc'])
      result_set['stability'].append(stat['s'])
      result_set['throughput'].append(stat['throughput'])
    # Calculate the CDF axises
    cdf_x, cdf_y = get_cdf_axises(result_set['convergence_time'])
    result_set['cdf_x'] = cdf_x
    result_set['cdf_y'] = cdf_y

    if figure_output == True:
      global_stats[key] = result_set

    print '----------------------------------------'
    print '%s:' % scenario[i]
    print_stats(result_set['average_cwnd'], result_set['convergence_time'],
                result_set['stability'], result_set['throughput'])

  # Plot CDF for convergence time
  if figure_output == True:
    font_size = 48
    fig_plot = plt.figure(algorithm + '-CDF-ConvergenceTime', figsize=(16, 9))
    ax1 = fig_plot.add_subplot(111)

    keys = []
    lines = []
    colors = []
    color_index = 0
    for r in range(0, len(rtt)):
      for l in range(0, len(loss)):
        k = 'RTT %sms, loss %s %%' % (rtt[r], loss[l])
        l = ax1.plot(global_stats[k]['cdf_x'], global_stats[k]['cdf_y'],
                     label='Wired, ' + k, linewidth=4,
                     color=line_color[color_index])
        color_index += 1
        keys.append(k)
        lines.append(l)
        colors.append(l[0].get_color())
    for i in range(1, len(scenario)):
      k = scenario[i]
      name = '2.4GHz, 802.11n' if k == '2.4g' else '5GHz, 802.11ac'
      l = ax1.plot(global_stats[k]['cdf_x'], global_stats[k]['cdf_y'],
                   label='Wireless, ' + name, linewidth=4,
                   color=line_color[color_index])
      color_index += 1
      keys.append(k)
      lines.append(l)
      colors.append(l[0].get_color())
    plt.xticks(np.arange(0, 120 + 20, 20), fontsize=font_size)
    plt.yticks(fontsize=font_size)
    plt.ylim(0, 1)

    plt.xlabel('Convergence Time (s)', fontsize=font_size)
    plt.ylabel('CDF', fontsize=font_size)

    plt.subplots_adjust(left=0.13, right=0.95, top=0.96, bottom=0.17)

    # Draw the legend in a separate figure
    if legend_out == True:
      handles, labels = ax1.get_legend_handles_labels()
      handles = [
          handles[0], handles[3], handles[6], handles[9],
          handles[1], handles[4], handles[7], handles[10],
          handles[2], handles[5], handles[8]
      ]
      labels = [
          labels[0], labels[3], labels[6], labels[9],
          labels[1], labels[4], labels[7], labels[10],
          labels[2], labels[5], labels[8]
      ]
      fig_legend = plt.figure(figsize=(16.5, 2.2))
      leg = fig_legend.legend(handles, labels, loc='center', ncol=3, fontsize=20)
      plt.axis('off')
      leg_lines = leg.get_lines()
      plt.setp(leg_lines, linewidth=8)
      fig_legend.canvas.draw()

    plt.show()


if __name__ == '__main__':
  main()
