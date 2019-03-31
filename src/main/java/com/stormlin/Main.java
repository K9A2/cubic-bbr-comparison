package com.stormlin;

import com.stormlin.util.Worker;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class Main {

    private static Logger logger = LogManager.getLogger();

    public static void main(String[] args) {

        int cores = Runtime.getRuntime().availableProcessors();
        logger.info("number of cores: " + cores);

        ExecutorService executor = Executors.newFixedThreadPool(cores);

        String[] lossArray = new String[]{"3", "5"};
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
