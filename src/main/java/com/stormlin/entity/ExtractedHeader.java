package com.stormlin.entity;

/**
 * 从每一行中提取的 TCP 包头信息, 包含收发双方的 IP, 端口号, 以及包长度.
 */
public class ExtractedHeader {
    public String seq;
    public String size;

    public String senderIp;
    public String senderPort;

    public String receiverIp;
    public String receiverPort;
}
