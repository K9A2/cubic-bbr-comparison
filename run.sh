#!/bin/bash

usage() {
  echo "Usage: specific all arguments below"
  echo "-c: congestion control (cc)"
  echo "-a: address"
  echo "-p: server port"
  echo "-d: duration, in second"
  echo "-r: rtt value, in ms"
  echo "-l: loss rate, in %"
  echo "-s: the start round"
  echo "-e: the end round"
  exit
}

log() {
  echo $(date "+%Y-%m-%d %H:%M:%S") ${1}
}

while getopts 'c:a:i:r:l:s:e:' OPT; do
  case $OPT in
    c) cc="$OPTARG";;
    a) address="$OPTARG";;
    # p) port="$OPTARG";;
    # i) nic="$OPTARG";;
    # d) duration="$OPTARG";;
    r) rtt="$OPTARG";;
    l) loss="$OPTARG";;
    s) start="$OPTARG";;
    e) end="$OPTARG";;
    ?) usage;;
  esac
done

for((i=${start};i<${end};i++));
do
  log "${cc} ${rtt}ms ${loss}% round: ${i}"
  echo ${cc} > /proc/sys/net/ipv4/tcp_congestion_control
  iperf3 -c ${address} -t 600 -J 1> \
    iperf3-${cc}-rtt${rtt}-loss${loss}-600s-${i}.json
  # give time to both side to fully finish the test
  sleep 60s
done

log "test finished"

