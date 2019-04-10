package com.stormlin.util;

class Constant {

    static final short DATA_PACKET_PAYLOAD = 1448;
    static final short PACKET_OVERHEAD_ON_WIRE = 66;


    static final String TCPDUMP_FILE_NAME_TEMPLATE = "tcpdump-%s-rtt%s-loss%s-1g-%s.log";
    static final String LOG_FILE_FORMAT = "runtime-log-%s-%s-%s.log";

    static final String ROLE_SENDER = "sender";
    static final String ROLE_RECEIVER = "receiver";

    // 当数据包发送次数大于等于 2 时, 认为发生了一次丢包
    static final byte DATA_PACKET_LOSS_THRESHOLD = 2;
    // 当 ack 数目大于等于 3 时, 认为发生了一次丢包
    static final byte ACK_LOSS_THRESHOLD = 3;

    private static final int KB = 1024;
    private static final int MB = KB * 1024;
    static final int GB = MB * 1024;

    static final String TASK_KEY = "%s @ rtt = %s, loss = %s";
    static final String MESSAGE_FORMAT = "%s - %s";
}
