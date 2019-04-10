package com.stormlin;

import com.stormlin.util.TerminalLogger;
import com.stormlin.util.Worker;
import org.apache.commons.io.FileUtils;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class Main {

    private static final TerminalLogger logger = TerminalLogger.getLogger();

    public static void main(String[] args) {

        // 创建或者清空日志文件夹
        Path logPath = Paths.get("./log/");
        try {
            if (Files.exists(logPath)) {
                FileUtils.cleanDirectory(new File(logPath.toUri()));
            } else if (!new File(logPath.toUri()).mkdir()) {
                logger.log("Unable to create log folder");
                return;
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

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
