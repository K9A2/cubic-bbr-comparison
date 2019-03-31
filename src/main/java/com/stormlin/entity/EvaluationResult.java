package com.stormlin.entity;

public class EvaluationResult {

    public double payloadSent;
    public double payloadRetransmitted;

    public int packetSent;
    public int packetRetransmitted;

    public int packetTransmittedTotal;

    public double onWireSentSender;
    public double onWireRetransmittedSender;
    public double onWireSentReceiver;
    public double onWireRetransmittedReceiver;
    public double onWireTotal;

    public double packetLossSender;
    public double packetLossReceiver;

    public double lossRatio;
    public double packetRetransmittedPerDataPacket;
    public double packetRetransmittedPerLossSender;
    public double packetRetransmittedPerLossReceiver;

    public double iperfThroughput;
    public double iperfDuration;
    public double iperfRetransmission;

}
