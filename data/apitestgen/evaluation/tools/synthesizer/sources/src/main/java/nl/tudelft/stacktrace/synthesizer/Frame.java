/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package nl.tudelft.stacktrace.synthesizer;

import com.google.common.base.Preconditions;

public class Frame {

    public static final int UNKOWN_LINE = -1;

    private String methodName;
    private int lineNumber;
    private String fileName;

    public Frame() {
    }
    
    public Frame(String methodName, int lineNumber, String fileName) {
        Preconditions.checkArgument(lineNumber > 0 || lineNumber == UNKOWN_LINE, "Given lineNumber must be greather than 0!");
        this.methodName = methodName;
        this.lineNumber = lineNumber;
        this.fileName = fileName;
    }

    public Frame(String methodName, String fileName) {
        this(methodName, UNKOWN_LINE, fileName);
    }

    public String getMethodName() {
        return methodName;
    }

    public int getLineNumber() {
        return lineNumber;
    }

    public String getFileName() {
        return fileName;
    }

    public void setMethodName(String methodName) {
        Preconditions.checkNotNull(methodName, "Given methodName may not be null!");
        this.methodName = methodName;
    }

    public void setLineNumber(int lineNumber) {
        Preconditions.checkArgument(lineNumber > 0 || lineNumber == UNKOWN_LINE, "Given lineNumber must be greather than 0!");
        this.lineNumber = lineNumber;
    }

    public void setFileName(String fileName) {
        Preconditions.checkNotNull(fileName, "Given fileName may not be null!");
        this.fileName = fileName;
    }

}
