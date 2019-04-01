package com.stormlin;

import com.stormlin.util.Worker;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.File;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class Main {

    private static Logger logger = LogManager.getLogger();

    public static void main(String[] args) {

        int cores = Runtime.getRuntime().availableProcessors();
        logger.info("number of cores: " + cores);

        File file = new File("./log/");
        try {
            if (!file.exists()) {
                if (!file.mkdir()) {
                    logger.error("Unable to create log folder.");
                }
            }
        } catch (Exception e) {
            logger.error("Unable to create log folder.");
            System.exit(1);
        }

        ExecutorService executor = Executors.newFixedThreadPool(1);

        String[] lossArray = new String[]{"0.1", "0.2", "0.4", "0.6", "0.8", "1"};
        for (String loss : lossArray) {
            Worker worker = new Worker("bbr", "200", loss);
            executor.execute(worker);
        }
        executor.shutdown();

        // 等待所有结束之后输出结果
        try {
            executor.awaitTermination(Long.MAX_VALUE, TimeUnit.MINUTES);
        } catch (InterruptedException e) {
            logger.error("Program interrupted");
        }

        logger.info("Program finished.");

    }
}
