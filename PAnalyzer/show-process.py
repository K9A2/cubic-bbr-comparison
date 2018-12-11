# -*- coding: utf-8 -*-
# filename: show-process.py

from python import libstorm as storm


def main():

    # rtt = ['12', '30', '60', '100', '200', '300']
    rtt = ['100', '200', '300']
    loss = ['0.01', '0.05', '0.1', '1.0', '3.0', '5.0']

    file_name_template = 'runtime-rtt%s-loss%s.log'

    storm.log('-------- Evaluation Process --------')

    for r in rtt:
        for l in loss:
            file_name = file_name_template % (r, l)
            lines = storm.read_text_file(file_name)
            length = len(lines)
            if length > 10:
                storm.log(file_name + ' DONE')
            else:
                storm.log(file_name + ' ROUND-' + str(length))
        storm.log('------------------------------------')


if __name__ == '__main__':
    main()
