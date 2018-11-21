# -*- coding: utf-8 -*-
# filename: show-process.py

import libstorm as storm


def main():

  rtt = ['12']
  loss = ['0.01', '0.1', '1', '3', '5']

  file_name_template = 'runtime-rtt%s-loss%s.log'

  storm.log('-------- Evaluation Process --------')

  for r in rtt:
    for l in loss:
      file_name = file_name_template % (r, l)
      lines = storm.read_text_file(file_name)
      length = len(lines)
      if length > 11:
        storm.log(file_name + ' DONE')
      else:
        storm.log(file_name + ' ROUND-' + str(length))
    storm.log('------------------------------------')


if __name__ == '__main__':
  main()

