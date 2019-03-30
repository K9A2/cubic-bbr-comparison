package com.stormlin.util;

public class Constant {

    public static final int DATA_PACKET_SIZE_ON_WIRE_IN_BYTE = 1514;
    public static final int PACKET_OVERHEAD_ON_WIRE = 66;

    public static final int DEFAULT_SERVER_PORT = 5201;

    public static final String TASK_STATUS_LOG_TEMPLATE = "Task \"%s, rtt=%s, loss=%s\", status=%s";
    public static final String RUNTIME_LOG_NAME_TEMPLATE = "runtime-%s-rtt%s-loss%s.log";

    public static final String IPERF_FILE_NAME_TEMPLATE = "./%s/iperf3-%s-rtt%s-loss%s-1g-%s.json";
    public static final String TCPDUMP_FILE_NAME_TEMPLATE = "tcpdump-%s-rtt%s-loss%s-1g-%s.log";

    public static final String ROLE_SENDER = "sender";
    public static final String ROLE_RECEIVER = "receiver";

    // 当数据包发送次数大于等于 2 时, 认为发生了一次丢包
    public static final int DATA_PACKET_LOSS_THRESHOLD = 2;
    // 当 ack 数目大于等于 3 时, 认为发生了一次丢包
    public static final int ACK_LOSS_THRESHOLD = 3;

    public static final String dateFormat = "yyyy-MM-dd HH:mm:ss";

}
