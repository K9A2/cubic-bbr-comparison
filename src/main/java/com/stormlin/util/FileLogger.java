package com.stormlin.util;

import java.io.FileWriter;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;

class FileLogger {

    private String fileName;
    private SimpleDateFormat formatter = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS");

    FileLogger(String fileName) {
        this.fileName = fileName;
    }

    void log(String message) {
        Date current = new Date();
        try {
            FileWriter writer = new FileWriter("./log/" + fileName, true);
            writer.write(formatter.format(current) + " " + message + "\n");
            writer.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
