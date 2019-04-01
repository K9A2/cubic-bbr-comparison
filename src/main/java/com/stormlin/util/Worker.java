package com.stormlin.util;

import com.stormlin.entity.EvaluationResult;
import com.stormlin.entity.ExtractedHeader;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;

public class Worker implements Runnable {

    private Logger logger;

    // 可重用的包头信息对象
    private ExtractedHeader header = new ExtractedHeader();
    // 提取的测试结果
    private HashMap<String, EvaluationResult> resultMap = new HashMap<>();

    private String algorithm;
    private String rtt;
    private String loss;

    public Worker(String algorithm, String rtt, String loss) {
        this.algorithm = algorithm;
        this.rtt = rtt;
        this.loss = loss;
        logger = new Logger(String.format(Constant.LOG_FILE_FORMAT, algorithm, rtt, loss));
    }

    /**
     * 分析收发双方的 tcpdump 日志记录
     */
    @Override
    public void run() {

        // 分析发送方的数据
        String fileName = String.format(Constant.TCPDUMP_FILE_NAME_TEMPLATE, algorithm, rtt, loss, Constant.ROLE_SENDER);
        analyze(fileName, Constant.ROLE_SENDER);

        // 分析接收方的数据
        fileName = String.format(Constant.TCPDUMP_FILE_NAME_TEMPLATE, algorithm, rtt, loss, Constant.ROLE_RECEIVER);
        analyze(fileName, Constant.ROLE_RECEIVER);

        // 输出测试结果
        outputEvaluationResult();
    }

    private void analyze(String fileName, String role) {

        HashMap<Long, Integer> dataPacket = new HashMap<>();

        File file = new File("./data/" + fileName);

        BufferedInputStream inputStream = null;
        try {
            inputStream = new BufferedInputStream(new FileInputStream(file));
        } catch (FileNotFoundException e) {
            logger.log("File: " + fileName + " not found");
        }
        if (inputStream == null) {
            return;
        }
        BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream, StandardCharsets.UTF_8));

        // 发送方 IP
        String senderIP = "";
        // 发送方端口号
        String senderPort = "";

        // 控制 socket 的端口号
        String controlSocketPort = "";
        // 数据 socket 的端口号
        String dataSocketPort = "";
        // 服务器监听的端口号
        String serverPort = "";

        String line;
        int count = 0;
        String resultKey = "";
        try {
            // 按行读取文件
            while ((line = reader.readLine()) != null) {
                extract(line, header);
                count += 1;
                // 本行的发送方端口号与已知的任何一个端口号均不相同, 则认为是新一次测试的开始, 需要重新设定部分参数
                if (!header.senderPort.equals(controlSocketPort) && !header.senderPort.equals(dataSocketPort) &&
                        !header.senderPort.equals(serverPort)) {
                    // 解析上一个测试的数据包发送记录
                    parsePacketHistory(dataPacket, resultKey, role);
                    // 为新测试清空数据集
                    dataPacket.clear();

                    // 更新基本变量
                    senderIP = header.senderIp;
                    controlSocketPort = header.senderPort;
                    serverPort = header.receiverPort;
                    // 查找数据 socket 的端口号
                    while ((line = reader.readLine()) != null) {
                        count += 1;
                        extract(line, header);
                        // 设置数据 socket 端口号
                        if (header.senderIp.equals(senderIP) && !header.senderPort.equals(controlSocketPort) &&
                                !header.senderPort.equals(senderPort)) {
                            dataSocketPort = header.senderPort;
                            break;
                        }
                    }
                    resultKey = controlSocketPort + "-" + dataSocketPort;
                    if (!resultMap.containsKey(resultKey)) {
                        EvaluationResult result = new EvaluationResult();
                        resultMap.put(resultKey, result);
                    }

                    logger.log("Detected new test at line " + count);
                    logger.log("controlSocketPort = " + controlSocketPort + ", dataSocketPort = " + dataSocketPort);
                }

                if (role.equals(Constant.ROLE_SENDER) && header.senderIp.equals(senderIP) &&
                        header.senderPort.equals(dataSocketPort)) {
                    // 数据包的序列号包含分号则表明此数据包为一个测试数据包
                    byte index = (byte) header.seq.indexOf(":");
                    if (index != -1) {
                        long seq = Long.parseLong(header.seq.substring(0, index));
                        if (dataPacket.containsKey(seq)) {
                            dataPacket.put(seq, dataPacket.get(seq) + 1);
                        } else {
                            dataPacket.put(seq, 1);
                        }
                    }
                } else if (role.equals(Constant.ROLE_RECEIVER) && header.receiverIp.equals(senderIP) &&
                        header.receiverPort.equals(dataSocketPort)) {
                    // 这是一个 ack 包
                    long ack = Long.parseLong(header.seq);
                    if (dataPacket.containsKey(ack)) {
                        dataPacket.put(ack, dataPacket.get(ack) + 1);
                    } else {
                        dataPacket.put(ack, 1);
                    }
                }
            }
            // 解析最后一次测试的数据包发送记录
            parsePacketHistory(dataPacket, resultKey, role);
        } catch (IOException e) {
            logger.log("IO exception");
        }
    }

    /**
     * 从数据包发送次数记录中提取结果
     *
     * @param dataPacket 数据包发送次数记录
     */
    private void parsePacketHistory(HashMap<Long, Integer> dataPacket, String resultKey, String role) {
        if (dataPacket.isEmpty() || resultKey.equals("")) {
            return;
        }
        EvaluationResult result = resultMap.get(resultKey);
        if (result == null) {
            return;
        }

        int payload;
        int threshold;
        int onWireSize;
        if (role.equals(Constant.ROLE_SENDER)) {
            payload = Constant.DATA_PACKET_PAYLOAD;
            threshold = Constant.DATA_PACKET_LOSS_THRESHOLD;
            onWireSize = Constant.DATA_PACKET_PAYLOAD + Constant.PACKET_OVERHEAD_ON_WIRE;
        } else {
            payload = 0;
            threshold = Constant.ACK_LOSS_THRESHOLD;
            onWireSize = Constant.PACKET_OVERHEAD_ON_WIRE;
        }
        // 解析记录并保存到全局记录集合中
        for (int value : dataPacket.values()) {
            if (role.equals(Constant.ROLE_SENDER)) {
                result.payloadSent += payload;
                result.packetSent += 1;
                result.onWireSentSender += onWireSize;
            } else {
                result.onWireSentReceiver += onWireSize;
            }
            if (value >= threshold) {
                if (role.equals(Constant.ROLE_SENDER)) {
                    // 数据包被重传
                    result.payloadRetransmitted += payload * (value - 1);
                    result.packetRetransmitted += (value - 1);
                    result.packetLossSender += 1;
                    result.onWireRetransmittedSender += onWireSize * (value - 1);
                } else {
                    // 确认包被重传
                    result.packetLossReceiver += 1;
                    result.onWireRetransmittedReceiver += onWireSize * (value - 1);
                }
            }
        }

        if (role.equals(Constant.ROLE_SENDER)) {
            result.packetTransmittedTotal = result.packetSent + result.packetRetransmitted;
            result.lossRatioSender = result.packetLossSender / result.packetSent;
            result.packetRetransmittedPerDataPacket = result.packetLossSender / result.packetSent;
            result.packetRetransmittedPerLossSender = result.packetRetransmitted / result.packetLossSender;
        } else {
            result.lossRatioReceiver = result.packetLossReceiver / result.packetSent;
            result.packetRetransmittedPerLossReceiver = result.packetRetransmitted / result.packetLossReceiver;
            result.onWireTotal = result.onWireSentReceiver + result.onWireRetransmittedSender +
                    result.onWireSentReceiver + result.onWireRetransmittedReceiver;
        }

    }

    /**
     * 输出测试结果
     */
    private void outputEvaluationResult() {
        if (resultMap.isEmpty()) {
            logger.log("Task " + algorithm + " @ rtt = " + rtt + ", loss = " + loss + " has not output!");
        }
        for (String resultKey : resultMap.keySet()) {
            EvaluationResult result = resultMap.get(resultKey);
            if (result == null) {
                return;
            }

            logger.log("----------------------------------------------------------------");
            logger.log("Info from " + algorithm + " @ rtt =" + rtt + ", loss = " + loss);
            logger.log("Evaluation Key = " + resultKey);
            logger.log("TCP Payload (Sent) = " + result.payloadSent / Constant.GB);
            logger.log("TCP Payload (Retransmitted) = " + result.payloadRetransmitted / Constant.GB);

            logger.log("Packet Sent (Sender) = " + result.packetSent);
            logger.log("Packet Retransmitted (Sender) = " + result.packetRetransmitted);
            logger.log("Packet Total (Sender) = " + result.packetTransmittedTotal);
            logger.log("Packet Loss (Sender) = " + result.packetLossSender);
            logger.log("Packet Loss (Receiver) = " + result.packetLossReceiver);

            logger.log("Loss Ratio (Sender) = " + result.lossRatioSender);
            logger.log("Loss Ratio (Receiver) = " + result.lossRatioReceiver);

            logger.log("Retransmission Per Data Packet = " + result.packetRetransmittedPerDataPacket);
            logger.log("Retransmission Per Loss (Sender) = " + result.packetRetransmittedPerLossSender);
            logger.log("Retransmission Per Loss (Receiver) = " + result.packetRetransmittedPerLossReceiver);

            logger.log("On-Wire Sent (Sender) = " + result.onWireSentSender / Constant.GB);
            logger.log("On-Wire Retransmitted (Sender) = " + result.onWireRetransmittedSender / Constant.GB);
            logger.log("On-Wire Sent (Receiver) = " + result.onWireSentReceiver / Constant.GB);
            logger.log("On-Wire Retransmitted (Sender) = " + result.onWireRetransmittedReceiver / Constant.GB);
            logger.log("On-Wire Total = " + result.onWireTotal / Constant.GB);
        }
    }

    /**
     * 从 tcpdump 日志文件的一行中提取收发双方的 IP, 端口号以及包大小
     *
     * @param line tcpdump 日志文件的一行
     */
    private void extract(String line, ExtractedHeader header) {
        String[] lineSplit = line.split(" ");

        header.seq = lineSplit[8].substring(0, lineSplit[8].length() - 1);
        header.size = lineSplit[lineSplit.length - 1];

        short lastIndex = (short) lineSplit[2].lastIndexOf('.');

        header.senderIp = lineSplit[2].substring(0, lastIndex);
        header.senderPort = lineSplit[2].substring(lastIndex + 1);

        lastIndex = (short) lineSplit[4].lastIndexOf('.');

        header.receiverIp = lineSplit[4].substring(0, lastIndex);
        header.receiverPort = lineSplit[4].substring(lastIndex + 1, lineSplit[4].length() - 1);
    }

}
