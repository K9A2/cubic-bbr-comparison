package com.stormlin;

import com.stormlin.util.TerminalLogger;
import com.stormlin.util.Worker;
import com.sun.xml.internal.ws.policy.privateutil.PolicyUtils;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class Main {

    private static final TerminalLogger logger = TerminalLogger.getLogger();
//    private static Logger logger = LogManager.getLogger();

    public static void main(String[] args) {

        int cores = Runtime.getRuntime().availableProcessors();
        logger.log("number of cores: " + cores);

        File configFile = new File("./config.txt");
        BufferedInputStream inputStream = null;
        try {
            inputStream = new BufferedInputStream(new FileInputStream(configFile));
        } catch (FileNotFoundException exception) {
            exception.printStackTrace();
        }
        if (inputStream == null) {
            logger.log("Unable to open input stream on config file");
            return;
        }
        BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream, StandardCharsets.UTF_8));
        ArrayList<String> lines = new ArrayList<>(4);
        String l;
        try {
            while ((l = reader.readLine()) != null) {
                lines.add(l);
            }
        } catch (IOException exception) {
            exception.printStackTrace();
        }
        String[] algorithmArray = lines.get(0).split(",");
        String[] rttArray = lines.get(1).split(",");
        String[] lossArray = lines.get(2).split(",");
        String dataFileFolder = lines.get(3);

        ExecutorService executor = Executors.newFixedThreadPool(cores);

//        String[] lossArray = new String[]{"0.1", "0.2", "0.4", "0.6", "0.8", "1", "3", "5"};
        for (String algorithm : algorithmArray) {
            for (String rtt : rttArray) {
                for (String loss : lossArray) {
                    Worker worker = new Worker(algorithm, rtt, loss, dataFileFolder);
                    executor.execute(worker);
                }
            }
        }
        executor.shutdown();

        // 等待所有结束之后输出结果
        try {
            executor.awaitTermination(Long.MAX_VALUE, TimeUnit.MINUTES);
        } catch (InterruptedException e) {
            logger.log("Program interrupted");
        }

        logger.log("Program finished.");

    }
}
