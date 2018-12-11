package java.com.stormlin;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.concurrent.locks.ReadWriteLock;

public class Worker implements Runnable {

    private static HashMap<String, Object> extractResult = new HashMap<>();
    private static ArrayList<HashMap<String, Integer>> roundSetList = new ArrayList<>();

    private List<String> algorithm;
    private List<String> rtt;
    private List<String> loss;

    private ReadWriteLock lock;

    Worker() {

    }

    private static HashMap<String, Integer> getDataset() {

        HashMap<String, Integer> result = new HashMap<>();

        result.put("payloadSent", 0);
        result.put("payloadRetransmitted", 0);

        result.put("packetSent", 0);
        result.put("packetRetransmitted", 0);

        result.put("onWireSent", 0);
        result.put("on_wire_retransmitted onWireRetransmitted", 0);

        result.put("packetLossSender", 0);
        result.put("packetLossReceiver", 0);

        // 用于 global data set 的字段
        result.put("onWireSentSender", 0);
        result.put("onWireRetransmittedSender", 0);
        result.put("onWireSentReceiver", 0);
        result.put("onWireRetransmittedReceiver", 0);
        result.put("onWireTotal", 0);

        return result;
    }

    private static void extract(String line) {
        String[] line_split = line.split("");

        extractResult.put("seq", line_split[8].substring(0, line_split[8].length() - 1));
        extractResult.put("size", Integer.parseInt(line_split[line_split.length - 1]));

        int last_index = line_split[2].lastIndexOf('.');

        extractResult.put("sip", line_split[2].substring(0, last_index));
        extractResult.put("sport", Integer.parseInt(line_split[2].substring(last_index + 1)));

        last_index = line_split[4].lastIndexOf('.');

        extractResult.put("rip", line_split[4].substring(0, last_index));
        extractResult.put("rport", Integer.parseInt(line_split[4].substring(last_index + 1)));
    }

    private static boolean isNewTest(int port, int cskp, int dskp) {
        return port != cskp && port != dskp && port != Constant.DEFAULT_SERVER_PORT;
    }

    private static int getDskp(int i, int length, List<String> lines, String iperf_sender_ip, int cskp) {
        for (int j = 0; j <= length; j++) {
            extract(lines.get(i));
            if (extractResult.get("sip").equals(iperf_sender_ip) && !extractResult.get("sport").equals(cskp)) {
                return (Integer) extractResult.get("sport");
            }
        }
        return 0;
    }

    private static void addNewPacket(String seq, int length, HashMap<String, Integer> roundSet,
                              HashMap<String, Integer> packetSet) {
        if (!packetSet.containsKey(seq)) {
            // 若给定的 seq 第一次出现, 则证明此数据包是第一次发送的, 需要为其创建 entry
            packetSet.put(seq, 0);
            roundSet.put("payload_sent", roundSet.get("payload_sent") + length);
            roundSet.put("packet_sent", roundSet.get("packet_sent") + 1);
            roundSet.put("on_wire_sent", roundSet.get("on_wire_sent") + (length + Constant.PACKET_OVERHEAD_ON_WIRE));
        } else {
            packetSet.put(seq, packetSet.get(seq) + 1);
            roundSet.put("packet_retransmitted", roundSet.get("packet_retransmitted") + 1);
            roundSet.put("on_wire_retransmitted",
                    roundSet.get("on_wire_retransmitted") + (length + Constant.PACKET_OVERHEAD_ON_WIRE));
        }

        packetSet.put(seq, packetSet.get(seq) + 1);
    }

    private static int getPacketLoss(HashMap<String, Integer> packetSet, int threshold) {
        int loss = 0;
        for (Integer value : packetSet.values()) {
            if (value >= threshold) {
                loss += 1;
            }
        }
        return loss;
    }

    private static boolean isDataSocket(String ip, int port, String iperfSenderIP, int dskp) {
        return ip.equals(iperfSenderIP) && port == dskp;
    }

    private static void analyze(List<String> lines, int length, HashMap<Integer, HashMap<String, Integer>> sideSet, String role,
                         HashMap<String, String> description) {

        String algorithm = description.get("algorithm");
        String rtt = description.get("rtt");
        String loss = description.get("loss");

        int nth_run = 1;

        extract(lines.get(0));

        String iperfSenderIP = (String) extractResult.get("sip");
        int cskp = (Integer) extractResult.get("sport");
        int dskp = getDskp(0, length, lines, iperfSenderIP, cskp);

        int key = cskp + dskp;

        sideSet.put(key, getDataset());

        HashMap<String, Integer> packetSet = new HashMap<>();

        for (int i = 1; i < length - 1; i++) {
            extract(lines.get(i));

            if (isNewTest((Integer) extractResult.get("sport"), (Integer) extractResult.get("cskp"),
                    (Integer) extractResult.get("dskp"))) {
                cskp = (Integer) extractResult.get("sport");
                dskp = getDskp(i, length, lines, iperfSenderIP, cskp);
                nth_run += 1;
                key = cskp + dskp;
                packetSet = null;
                sideSet.put(key, getDataset());
            }

            if (isDataSocket((String) extractResult.get("sip"), (Integer) extractResult.get("sport"),
                    iperfSenderIP, dskp) && role.equals("sender")) {
                addNewPacket((String) extractResult.get("seq"), (Integer) extractResult.get("size"), sideSet.get(key),
                        packetSet);
            } else if (isDataSocket((String) extractResult.get("rip"), (Integer) extractResult.get("rport"),
                    iperfSenderIP, dskp) && role.equals("receiver")) {
                addNewPacket((String) extractResult.get("seq"), (Integer) extractResult.get("size"), sideSet.get(key),
                        packetSet);
            }
        }

        // TODO: 调用 getLoss 方法来计算收发双方的丢包数
    }

    private static HashMap<Integer, Integer> getGlobalStats(HashMap<Integer, HashMap<String, Integer>> senderStats,
                                                           HashMap<Integer, HashMap<String, Integer>> receiverStats) {
        HashMap<Integer, Integer> globalStats = new HashMap<>();

        float payloadSent = 0.0f;
        float payloadRetransmitted = 0.0f;

        float packetSent = 0.0f;
        float packetRetransmitted = 0.0f;

        float packetLossSender = 0.0f;
        float packetLossReceiver = 0.0f;

        float onWireSentSender = 0.0f;
        float onWireRetransmittedSender = 0.0f;
        float onWireSentReceiver = 0.0f;
        float onWireRetransmittedReceiver = 0.0f;

        // 由于收发双方的 key 值是相同的, 故直接采用发送方的 keySet 来建立全局数据集
//        for (Integer key : senderStats.keySet()) {
//            globalStats.put(key, getDataset());
//
//
//        }

        return globalStats;
    }

//    private static void printGloablStats(HashMap<Integer, In>)

    public void run() {

        lock.readLock().lock();



    }

}
