package com.stormlin.util;

import com.stormlin.entity.EvaluationResult;
import com.stormlin.entity.ExtractedHeader;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;

public class Worker implements Runnable {

    private static final Logger logger = LogManager.getLogger();

    // 可重用的包头信息对象
    private ExtractedHeader header = new ExtractedHeader();
    // 可重用的数据包计数
    private HashMap<Integer, Integer> dataPacket = new HashMap<>();
    // 提取的测试结果
    private HashMap<String, EvaluationResult> resultMap = new HashMap<>();

    private String algorithm;
    private String rtt;
    private String loss;

    public Worker(String algorithm, String rtt, String loss) {
        this.algorithm = algorithm;
        this.rtt = rtt;
        this.loss = loss;
    }

    /**
     * 分析收发双方的 tcpdump 日志记录
     */
    @Override
    public void run() {

        String fileName = String.format(Constant.TCPDUMP_FILE_NAME_TEMPLATE, algorithm, rtt, loss, Constant.ROLE_SENDER);
        File file = new File("./data/" + fileName);

        BufferedInputStream inputStream = null;
        try {
            inputStream = new BufferedInputStream(new FileInputStream(file));
        } catch (FileNotFoundException e) {
            logger.error("File: " + fileName + " not found");
        }
        if (inputStream == null) {
            return;
        }
        BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream, StandardCharsets.UTF_8));

        // 发送方 IP
        String senderIP;
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
                    parsePacketHistory(dataPacket, resultKey);
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
                    EvaluationResult result = new EvaluationResult();
                    resultMap.put(resultKey, result);

                    logger.info("Detected new test at line " + count);
                    logger.info("controlSocketPort = " + controlSocketPort + ", dataSocketPort = " + dataSocketPort);
                }

                // 数据包的序列号包含分号则表明此数据包为一个测试数据包
                byte index = (byte) header.seq.indexOf(":");
                if (index != -1) {
                    int seq = Integer.parseInt(header.seq.substring(0, index));
                    if (dataPacket.containsKey(seq)) {
                        dataPacket.put(seq, dataPacket.get(seq) + 1);
                    } else {
                        dataPacket.put(seq, 1);
                    }
                }
            }
            // 解析最后一次测试的数据包发送记录
            parsePacketHistory(dataPacket, resultKey);
        } catch (IOException e) {
            logger.error("IO exception");
        }

        // 输出测试结果
        outputEvaluationResult();

        logger.info(count + " line scanned");
    }

    /**
     * 从数据包发送次数记录中提取结果
     *
     * @param dataPacket 数据包发送次数记录
     */
    private void parsePacketHistory(HashMap<Integer, Integer> dataPacket, String resultKey) {
        if (dataPacket.isEmpty() || resultKey.equals("")) {
            return;
        }
        EvaluationResult result = resultMap.get(resultKey);
        if (result == null) {
            return;
        }

        // 解析记录并保存到全局记录集合中
        for (int value : dataPacket.values()) {
            result.payloadSent += Constant.DATA_PACKET_PAYLOAD;
            result.packetSent += 1;
            result.onWireSentSender += Constant.DATA_PACKET_SIZE_ON_WIRE_IN_BYTE + Constant.PACKET_OVERHEAD_ON_WIRE;
            if (value >= Constant.DATA_PACKET_LOSS_THRESHOLD) {
                // 数据包被重传
                result.payloadRetransmitted += Constant.DATA_PACKET_PAYLOAD * (value - 1);
                result.packetRetransmitted += (value - 1);
                result.packetLossSender += 1;
                result.onWireRetransmittedSender +=
                        (Constant.DATA_PACKET_SIZE_ON_WIRE_IN_BYTE + Constant.PACKET_OVERHEAD_ON_WIRE) * (value - 1);

            }
        }

        result.packetTransmittedTotal = result.packetSent + result.packetRetransmitted;
        result.onWireTotal = result.onWireSentReceiver + result.onWireRetransmittedSender;
        result.lossRatio = result.packetLossSender / (result.packetSent + result.packetRetransmitted);
        result.packetRetransmittedPerDataPacket = result.packetLossSender / result.packetSent;
        result.packetRetransmittedPerLossSender = result.packetLossSender / result.packetLossSender;
    }

    /**
     * 输出测试结果
     */
    private void outputEvaluationResult() {
        if (resultMap.isEmpty()) {
            logger.error("Task " + algorithm + " @ rtt = " + rtt + ", loss = " + loss + " has not output!");
        }
        for (String resultKey : resultMap.keySet()) {
            EvaluationResult result = resultMap.get(resultKey);
            if (result == null) {
                return;
            }

            logger.info("Info from " + algorithm + " @ rtt =" + rtt + ", loss = " + loss);
            logger.info("Evaluation Key = " + resultKey);
            logger.info("TCP Payload (Sent) = " + result.payloadSent / Constant.GB);
            logger.info("TCP Payload (Retransmitted) = " + result.payloadRetransmitted / Constant.GB);

            logger.info("Packet Sent (Sender) = " + result.packetSent);
            logger.info("Packet Retransmitted (Sender) = " + result.packetRetransmitted);
            logger.info("Packet Total (Sender) = " + result.packetTransmittedTotal);
            logger.info("Packet Loss (Sender) = " + result.packetLossSender);

            logger.info("Loss Ratio (Sender) = " + result.lossRatio);

            logger.info("Retransmission Per Data Packet = " + result.packetRetransmittedPerDataPacket);
            logger.info("Retransmission Per Loss (Sender) = " + result.packetRetransmittedPerLossSender);

            logger.info("On-Wire Sent (Sender) = " + result.onWireSentSender / Constant.GB);
            logger.info("On-Wire Retransmitted (Sender) = " + result.onWireRetransmittedSender / Constant.GB);
            logger.info("On-Wire Total (Sender) = " + result.onWireTotal / Constant.GB);

            logger.info("----------------------------------------------------------------");
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
