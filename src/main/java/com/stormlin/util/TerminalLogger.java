package com.stormlin.util;

import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * 向命令行打印日志的 Logger
 */
public class TerminalLogger {

    private SimpleDateFormat formatter = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS");
    private static TerminalLogger logger = new TerminalLogger();

    private TerminalLogger() {
    }

    public static TerminalLogger getLogger() {
        return logger;
    }

    /**
     * 向命令行输出日志信息
     */
    public void log(String message) {
        Date now = new Date();
        System.out.println(formatter.format(now) + " - " + message);
    }

}
