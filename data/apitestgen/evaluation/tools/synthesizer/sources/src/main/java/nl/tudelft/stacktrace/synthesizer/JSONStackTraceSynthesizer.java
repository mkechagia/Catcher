package nl.tudelft.stacktrace.synthesizer;

import com.google.common.base.Preconditions;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Synthesize a set of stack traces for one JSON entry. For example :
 * <pre>
 * {@code
 * { "org.apache.commons.lang3.StringUtils.getLevenshteinDistance(java.lang.CharSequence,java.lang.CharSequence,int)-java.util.Arrays.fill(int[], * int, int, int)":
 * { "call-site-sig":"org.apache.commons.lang3.StringUtils.getLevenshteinDistance(java.lang.CharSequence,java.lang.CharSequence,int)",
 *   "exception-list": "['java.lang.IllegalArgumentException','java.lang.ArrayIndexOutOfBoundsException']",
 *   "api-method-sig":"java.util.Arrays.fill(int[], int, int, int)",
 *   "call-site-line": "8209",
 *   "api-method-line": "2902",
 *   "java-file-path": "StringUtils.java",
 *   "java-method-sig": "java.math.BigInteger.pow(int)",
 *   "java-method-line": "42" }
 * } }
 * </pre>
 *
 * @author Xavier Devroey - xavier.devroey@gmail.com
 */
public class JSONStackTraceSynthesizer implements StackTraceSynthesizer {

    private static final Logger LOG = LoggerFactory.getLogger(JSONStackTraceSynthesizer.class);

    private static final String EXCEPTIONS_LIST_FIELD = "exception-list";
    private static final String LEVEL_0 = "level_0";
    private static final String LEVEL_1 = "level_1";
    private static final String LEVEL_2 = "level_2";

    private static final String CALLLER_SIG_FIELD = "call-site-sig";
    private static final String CALLLER_LINE_FIELD = "call-site-line";

    private static final String API_SIG_FIELD = "api-method-sig";
    //private static final String API_LINE_FIELD = "api-method-line";

    public JSONStackTraceSynthesizer() {
        super();
    }

    @Override
    public List<StackTrace> synthesize(String input) {
        JsonParser parser = new JsonParser();
        Set<Map.Entry<String, JsonElement>> entries = parser.parse(input).getAsJsonObject().entrySet();
        Preconditions.checkArgument(entries.size() == 1, "Has %i entries, cannot have more than one entry in JSON input!", entries.size());
        JsonObject entry = entries.iterator().next().getValue().getAsJsonObject();
        return synthesize(entry);
    }

    public List<StackTrace> synthesize(JsonObject input) {
        List<StackTrace> traces = getAPIStackTraces(input);
        Frame callSiteFrame = getCallSiteFrame(input);
        // Add call site frame
        traces.forEach((t) -> {
            t.addFrame(callSiteFrame);
        });
        LOG.trace("Number of stack traces syntesized: {}", traces.size());
        return traces;
    }

    private List<StackTrace> getAPIStackTraces(JsonObject input) {
        List<StackTrace> traces = new ArrayList<>();
        // Get the method frame info
        String sig = input.get(API_SIG_FIELD).getAsString();
        LOG.trace("API callee signature: {}", sig);
        Preconditions.checkNotNull(sig, "Field %s may not be null!", API_SIG_FIELD);
        String methodName = sig.split("\\(")[0];
        LOG.trace("API callee method name: {}", methodName);
        Preconditions.checkNotNull(methodName, "Method name may not be null!");
        String fileName = getFileName(methodName);
        LOG.trace("API callee file name: {}", fileName);
        // Level0 has one level less array
        for (JsonElement element : input.getAsJsonObject(EXCEPTIONS_LIST_FIELD).getAsJsonArray(LEVEL_0)) {
            traces.add(processLevel0(methodName, fileName, element.getAsJsonArray()));
        }
        // Levels 1 and 2
        for (String level : new String[]{LEVEL_1, LEVEL_2}) {
            for (JsonElement tab : input.getAsJsonObject(EXCEPTIONS_LIST_FIELD).getAsJsonArray(level)) {
                traces.add(processHigherLevel(methodName, fileName, tab.getAsJsonArray()));
            }
        }
        return traces;
    }

    private StackTrace processLevel0(String methodName, String fileName, JsonArray element) {
        String exceptionName = element.get(1).getAsString();
        LOG.trace("Exception name: {}", exceptionName);
        Preconditions.checkNotNull(exceptionName, "Exception name may not be null!");
        StackTrace stackTrace = new StackTrace(exceptionName);
        int line = Integer.parseInt(element.get(0).getAsString());
        stackTrace.addFrame(new Frame(methodName, line, fileName));
        return stackTrace;
    }
    
    private StackTrace processHigherLevel(String methodName, String fileName, JsonArray tab) {
        JsonArray element = tab.get(tab.size() - 1).getAsJsonArray();
        String exceptionName = element.get(1).getAsString();
        LOG.trace("Exception name: {}", exceptionName);
        Preconditions.checkNotNull(exceptionName, "Exception name may not be null!");
        StackTrace stackTrace = new StackTrace(exceptionName);
        // Initialise the line for the next element
        int line = Integer.parseInt(element.get(0).getAsString());
        // Start from the last - 1 element (last element contains the exception thrown)
        for (int i = tab.size() - 2; 0 <= i ; i--) {
            element = tab.get(i).getAsJsonArray();
            String sig = element.get(1).getAsString();
            LOG.trace("API callee signature: {}", sig);
            Preconditions.checkNotNull(sig, "API callee signature may not be null!");
            String calleeName = sig.split("\\(")[0];
            LOG.trace("API callee method name: {}", calleeName);
            Preconditions.checkNotNull(calleeName, "Method name may not be null!");
            String calleeFileName = getFileName(calleeName);
            LOG.trace("API callee file name: {}", calleeFileName);
            // add frame 
            stackTrace.addFrame(new Frame(calleeName, line, calleeFileName));
            // update line for the next element             
            line = Integer.parseInt(element.get(0).getAsString());
        }
        stackTrace.addFrame(new Frame(methodName, line, fileName));
        return stackTrace;
    }

    private Frame getCallSiteFrame(JsonObject input) {
        String methodName;
        String fileName;
        int line;
        String sig = input.get(CALLLER_SIG_FIELD).getAsString();
        LOG.trace("Client caller signature: {}", sig);
        Preconditions.checkNotNull(sig, "Field {} may not be null!", CALLLER_SIG_FIELD);
        // Get method name
        methodName = sig.split("\\(")[0];
        LOG.trace("Client caller method name: {}", methodName);
        Preconditions.checkNotNull(methodName, "Method name may not be null!");
        // Get file name
        fileName = getFileName(methodName);
        LOG.trace("Client caller file name: {}", methodName);
        // Get line number
        line = input.get(CALLLER_LINE_FIELD).getAsInt();
        LOG.trace("Client caller line: {}", line);
        return new Frame(methodName, line, fileName);
    }

    private String getFileName(String methodName) {
        String[] parts = methodName.split("\\.");
        return parts[parts.length - 2].split("\\$")[0].concat(".java");
    }

}
