#!/bin/bash

usage() {
  echo "Usage: specific all arguments below"
  echo "-c: congestion control (cc)"
  echo "-a: address"
  echo "-p: server port"
  echo "-d: duration, in second"
  echo "-r: rtt value, in ms"
  echo "-l: loss rate, in %"
  echo "-f: frequency, used to set log name"
  echo "-s: the start round"
  echo "-e: the end round"
  exit
}

log() {
  echo $(date "+%Y-%m-%d %H:%M:%S") ${1}
}

while getopts 'c:a:f:s:e:' OPT; do
  case $OPT in
    # The congestion control protocol (cc) needed to be specified
    c) cc="$OPTARG";;
    # The address of iperf3 server
    a) address="$OPTARG";;
    # Use the value of frequency to set the log file name
    f) frequency="$OPTARG"
    # The beginning of this evaluation group
    s) start="$OPTARG";;
    # The end of this evaluation group
    e) end="$OPTARG";;
    ?) usage;;
  esac
done

log "task started"

for((i=${start};i<${end};i++));
do
  log "${cc} frequency ${frequency} round: ${i}"
  echo ${cc} > /proc/sys/net/ipv4/tcp_congestion_control
  iperf3 -c ${address} -t 600 -J 1> \
    iperf3-${cc}-frequency${frequency}-600s-${i}.json
  # give time to both side to fully finish the test
  sleep 60s
done

log "test finished"
