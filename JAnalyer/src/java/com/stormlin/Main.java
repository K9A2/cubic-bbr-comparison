package java.com.stormlin;

public class Main {

    public int DATA_PACKET_SIZE_ON_WIRE_IN_BYTE = 1000;
    public int PACKET_OVERHEAD_ON_WIRE = 66;

    public String DEFAULT_SERVER_PORT = "5201";

    public String TASK_STATUS_LOG_TEMPLATE = "Task \"%s, rtt=%s, loss=%s\", status=%s";
    public String RUNTIME_LOG_NAME_TEMPLATE = "runtime-%s-rtt%s-loss%s.log";

    public String IPERF_FILE_NAME_TEMPLATE = "./%s/iperf3-%s-rtt%s-loss%s-1g-%s.json";
    public String TCPDUMP_FILE_NAME_TEMPLATE = "./%s/tcpdump-%s-rtt%s-loss%s-1g-%s.log";

    // 当数据包发送次数大于等于 2 时, 认为发生了一次丢包
    public int DATA_PACKET_LOSS_THRESHOLD = 2;
    // 当 ack 数目大于等于 3 时, 认为发生了一次丢包
    public int ACK_LOSS_THRESHOLD = 3;

    public static void main(String[] args) {

        System.out.println(System.getProperty("user.dir"));

    }
}
