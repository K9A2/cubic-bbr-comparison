package com.stormlin.entity;

public class EvaluationResult {

    /* 特指数据 socket 中的数据包. 控制 socket 不予考虑. */

    // 发送方应当被发送的 TCP payload, 不含被重传的 TCP payload
    public float payloadSent;
    // 发送方重传的所有数据包的 TCP payload 之和
    public float payloadRetransmitted;

    // 发送方发送的应当发送的数据包数目
    public float packetSent;
    // 发送方重传过的数据包数目
    public float packetRetransmitted;
    // 发送方发送过的所有数据包的数目
    public float packetTransmittedTotal;

    // 发送方应当发送的数据包在以太网上的总大小
    public float onWireSentSender;
    // 发送方重传的数据包在以太网上的总大小
    public float onWireRetransmittedSender;
    // 接收方在以太网上发送的 ack 总大小
    public float onWireSentReceiver;
    // 接收方在以太网上重传的 ack 总大小
    public float onWireRetransmittedReceiver;
    // 收发双方通过以太网传送的数据量大小
    public float onWireTotal;

    // 发送方确认的丢包次数
    public float packetLossSender;
    // 接收方确认的丢包次数
    public float packetLossReceiver;

    // 发送方测量的丢包率
    public float lossRatioSender;
    // 接收方测量的丢包率
    public float lossRatioReceiver;

    // 以发送方数据衡量的平均每个数据包发生了多少次重传数
    public float packetRetransmittedPerDataPacket;
    // 以发送方数据衡量的平均每次丢包所需要重传的数据包个数
    public float packetRetransmittedPerLossSender;
    // 以接收方数据衡量的平均每次丢包所需要重传的数据包个数
    public float packetRetransmittedPerLossReceiver;

    // 来自 iperf3 的测试结果
    public double iperfThroughput;
    public double iperfDuration;
    public double iperfRetransmission;

}
