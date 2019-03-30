package com.stormlin;

import com.stormlin.entity.ExtractedHeader;
import com.stormlin.util.Constant;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.HashMap;

public class Worker implements Runnable {

    private ExtractedHeader header = new ExtractedHeader();
    private HashMap<String, Object> extractResult = new HashMap<>();
    private ArrayList<HashMap<String, Integer>> roundSetList = new ArrayList<>();

    private HashMap<String, Integer> packetSentCount = new HashMap<>();

    private String algorithm;
    private String rtt;
    private String loss;

    Worker(String algorithm, String rtt, String loss) {
        this.algorithm = algorithm;
        this.rtt = rtt;
        this.loss = loss;
    }

    /**
     * Extract fields from string
     *
     * @param line On line from tcpdump file
     */
    private void extract(String line, ExtractedHeader result) {
        String[] lineSplit = line.split(" ");

        header.seq = lineSplit[8].substring(0, lineSplit[8].length() - 1);
        header.size = lineSplit[lineSplit.length - 1];

        int lastIndex = lineSplit[2].lastIndexOf('.');

        header.senderIp = lineSplit[2].substring(0, lastIndex);
        header.senderPort = lineSplit[2].substring(lastIndex + 1);

        lastIndex = lineSplit[4].lastIndexOf('.');

        header.receiverIp = lineSplit[4].substring(0, lastIndex);
        header.receiverPort = lineSplit[4].substring(lastIndex + 1, lineSplit[4].length() - 1);
    }

    /**
     * Whether the line belongs to a new test. A test is identified by controlSocketPort and dataSocketPort.
     * controlSocketPort and dataSocketPort will not remain the same between tests.
     *
     * @param port              The post extracted from tcpdump line record
     * @param controlSocketPort Control socket port of iperf3 test
     * @param dataSocketPort    Data socket port of iperf3 test
     * @return Whether the line belongs to the latest test.
     */
    private static boolean isNewTest(int port, int controlSocketPort, int dataSocketPort) {
        return port != controlSocketPort && port != dataSocketPort && port != Constant.DEFAULT_SERVER_PORT;
    }

//    /**
//     * Get the data socket port dynamically from line record.
//     * @param i
//     * @param length
//     * @param lines
//     * @param iperf_sender_ip
//     * @param cskp
//     * @return
//     */
//    private static int getDataSocketPort(int i, int length, List<String> lines, String iperf_sender_ip, int cskp) {
//        for (int j = 0; j <= length; j++) {
//            extract(lines.get(i));
//            if (extractResult.get("sip").equals(iperf_sender_ip) && !extractResult.get("sport").equals(cskp)) {
//                return (Integer) extractResult.get("sport");
//            }
//        }
//        return 0;
//    }

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

    /**
     * Analyze a dump file at a time
     */
    private void analyze() {

        String fileName = String.format(Constant.TCPDUMP_FILE_NAME_TEMPLATE, algorithm, rtt, loss, Constant.ROLE_SENDER);
        File file = new File("./data/" + fileName);
        BufferedInputStream inputStream = null;

        try {
            inputStream = new BufferedInputStream(new FileInputStream(file));
        } catch (FileNotFoundException e) {
            System.out.println("File \"" + "./data/" + fileName + "\" not found.");
        }
        if (inputStream == null) {
            return;
        }
        BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream, StandardCharsets.UTF_8), 5 * 1024 * 1024);

        String line;
        int count;
        ExtractedHeader extractedResult = new ExtractedHeader();
        try {
            while ((line = reader.readLine()) != null) {
                extract(line, extractedResult);
                if (packetSentCount.containsKey(header.seq)) {
                    count = packetSentCount.get(header.seq);
                    packetSentCount.put(header.seq, count + 1);
                }
                packetSentCount.put(header.seq, 1);
            }
        } catch (IOException e) {
            System.out.println("IO exception");
        }
        System.out.println(packetSentCount.size());
        int retransmittedPacketCount = 0;
        for (HashMap.Entry<String, Integer> entry : packetSentCount.entrySet()) {
            if (packetSentCount.get(entry.getKey()) > 3) {
                retransmittedPacketCount += 1;
            }
        }
        System.out.println(retransmittedPacketCount);
    }

    public void run() {
        LocalTime startTime = LocalTime.now();
        System.out.println(startTime.toString());
        analyze();
        LocalTime endTime = LocalTime.now();
        System.out.println(endTime.toString());
    }

}
