package nl.tudelft.stacktrace.synthesizer;

import java.util.List;

/**
 * An abstract stack trace synthesizer. Synthesize a stack traces for a location
 * and one method call. If one method call may throw more than one exception,
 * one stack trace is synthesized for each exception.
 *
 * @author Xavier Devroey - xavier.devroey@gmail.com
 */
public interface StackTraceSynthesizer {

    public List<StackTrace> synthesize(String input);

}


