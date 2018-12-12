#!/bin/bash

rm *.json
rm *.log
python kill-iperf.py
mn -c

