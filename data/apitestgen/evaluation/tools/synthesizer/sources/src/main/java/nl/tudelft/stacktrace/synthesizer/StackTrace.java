package nl.tudelft.stacktrace.synthesizer;

import com.google.common.base.Preconditions;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

public class StackTrace implements Iterable<Frame>{

    private final String exceptionName;
    private final List<Frame> frames;
    
    public static final String UNKNOWN_SOURCE = "Unknown Source";

    public StackTrace(String exceptionName) {
        Preconditions.checkNotNull(exceptionName, "Given exceptionName may not be null!");
        this.exceptionName = exceptionName;
        this.frames = new ArrayList<>();
    }

    public String getExceptionName() {
        return exceptionName;
    }
    
    public StackTrace addFrame(Frame f){
        Preconditions.checkNotNull(f, "Given frame f may not be null!");
        frames.add(f);
        return this;
    }
    
    public Frame getFrame(int i){
        Preconditions.checkElementIndex(i, frames.size());
        return frames.get(i);
    }
    
    public int getFramesCount(){
        return frames.size();
    }

    @Override
    public Iterator<Frame> iterator() {
        return frames.iterator();
    }

    @Override
    public String toString() {
        StringBuilder builder = new StringBuilder();
        builder = builder.append(getExceptionName()).append(':').append('\n');
        for(Frame f : this.frames){
            builder = builder.append("\tat ").append(f.getMethodName());
            if(f.getLineNumber() == Frame.UNKOWN_LINE){
                builder = builder.append('(').append(UNKNOWN_SOURCE).append(')');
            } else {
                builder = builder.append('(').append(f.getFileName()).append(':').append(f.getLineNumber()).append(')');
            }
            builder = builder.append('\n');
        }
        return builder.toString();
    }
    
}
