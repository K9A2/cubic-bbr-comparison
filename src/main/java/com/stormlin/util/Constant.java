package com.stormlin.util;

import java.text.DecimalFormat;

public class Constant {

    public static final int DATA_PACKET_SIZE_ON_WIRE_IN_BYTE = 1514;
    public static final int DATA_PACKET_PAYLOAD = 1448;
    public static final int PACKET_OVERHEAD_ON_WIRE = 66;

    public static final String DEFAULT_SERVER_PORT = "5201";

    public static final String TASK_STATUS_LOG_TEMPLATE = "Task \"%s, rtt=%s, loss=%s\", status=%s";
    public static final String RUNTIME_LOG_NAME_TEMPLATE = "runtime-%s-rtt%s-loss%s.log";

    public static final String IPERF_FILE_NAME_TEMPLATE = "./%s/iperf3-%s-rtt%s-loss%s-1g-%s.json";
    public static final String TCPDUMP_FILE_NAME_TEMPLATE = "tcpdump-%s-rtt%s-loss%s-1g-%s.log";
    public static final String LOG_FILE_FORMAT = "runtime-log-%s-%s-%s.log";

    public static final String ROLE_SENDER = "sender";
    public static final String ROLE_RECEIVER = "receiver";

    // 当数据包发送次数大于等于 2 时, 认为发生了一次丢包
    public static final byte DATA_PACKET_LOSS_THRESHOLD = 2;
    // 当 ack 数目大于等于 3 时, 认为发生了一次丢包
    public static final byte ACK_LOSS_THRESHOLD = 3;

    public static final int KB = 1024;
    public static final int MB = KB * 1024;
    public static final int GB = MB * 1024;

    public static final String TASK_KEY = "%s @ rtt = %s, loss = %s";
    public static final String MESSAGE_FORMAT = "%s - %s";

    public static final DecimalFormat PERCENTAGE_FORMAT = new DecimalFormat("0.00");

}
