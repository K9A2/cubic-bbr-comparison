# README

This is a comparative evaluation on the thorughput and retransmission of CUBIC
and BBR in the TCP layer/ON-WIRE.

The evaluation is carried out as follows:
- We use Mininet to set up the simulated network with topology specified in 
[full-topology.py](./full-topology.py), which composed with dumbbell network
with different RTT and loss rate. 
- Then we user [iperf3](https://github.com/esnet/iperf) 
to start the evaluation between the sender and receiver. Before starting the
evaluation, we also get ready the tcpdump at both sides and set them to capture
the TCP packets.
- After the evaluation, we use the [tcpdump.py](./tcpdump.py) to analyze the
dumpfiles as well as the JSON files provided by iperf3.

