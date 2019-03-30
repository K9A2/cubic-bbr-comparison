package com.stormlin.entity;

public class ResultSet {

    double payloadSent = 0;
    double pyaloadRetransmitted = 0;

    double packetSent = 0;
    double packetRetransmitted = 0;

    double onWireSentSender = 0;
    double onWireRetransmittedSender = 0;
    double onWireSentReceiver = 0;
    double onWireRetransmittedReceiver = 0;

    double packetLossSender = 0;
    double packetLossReceiver = 0;

    double ratio = 0;

    double iperfThroughput = 0;
    double iperfDuration = 0;
    double iperfRetransmission = 0;

}
