package nl.tudelft.stacktrace.synthesizer;

import java.util.List;
import org.junit.Test;
import static org.junit.Assert.*;
import static org.hamcrest.Matchers.*;
import org.junit.Rule;
import org.junit.rules.TestRule;
import org.junit.rules.TestWatcher;
import org.junit.runner.Description;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 *
 * @author Xavier Devroey - xavier.devroey@gmail.com
 */
public class JSONStackTraceSynthesizerTest {

    private static final Logger LOG = LoggerFactory.getLogger(JSONStackTraceSynthesizerTest.class);

    @Rule
    public TestRule watcher = new TestWatcher() {
        @Override
        protected void starting(Description description) {
            LOG.info(String.format("Starting test: %s()...",
                    description.getMethodName()));
        }
    ;

    };

    public JSONStackTraceSynthesizerTest() {
    }

    @Test
    public void testSynthesize() {
        String input = "{\"org.jfree.chart.renderer.xy.StandardXYItemRenderer.readObject(java.io.ObjectInputStream)-java.io.ObjectInputStream.defaultReadObject()\": {\n"
                + "        \"call-site-sig\": \"org.jfree.chart.renderer.xy.StandardXYItemRenderer.readObject(java.io.ObjectInputStream)\", \n"
                + "        \"exception-list\": {\n"
                + "            \"level_0\": [\n"
                + "                [\n"
                + "                    \"553\", \n"
                + "                    \"java.io.NotActiveException\"\n"
                + "                ],\n"
                + "                [\n"
                + "                    \"554\", \n"
                + "                    \"java.io.NotActiveException2\"\n"
                + "                ]\n"
                + "            ], \n"
                + "            \"level_1\": [], \n"
                + "            \"level_2\": [], \n"
                + "            \"id\": \"java.io.ObjectInputStream.defaultReadObject()\"\n"
                + "        }, \n"
                + "        \"api-method-sig\": \"java.io.ObjectInputStream.defaultReadObject()\", \n"
                + "        \"call-site-line\": \"1056\", \n"
                + "        \"java-file-path\": \"StandardXYItemRenderer.java\"\n"
                + "    }}";
        List<StackTrace> traces = new JSONStackTraceSynthesizer().synthesize(input);
        assertThat(traces, hasSize(2));
        for (StackTrace trace : traces) {
            assertThat(trace.getFramesCount(), equalTo(2));
            Frame apiFrame = trace.getFrame(0);
            assertThat(apiFrame.getMethodName(), equalTo("java.io.ObjectInputStream.defaultReadObject"));
            assertThat(apiFrame.getFileName(), equalTo("ObjectInputStream.java"));
            Frame callerFrame = trace.getFrame(1);
            assertThat(callerFrame.getMethodName(), equalTo("org.jfree.chart.renderer.xy.StandardXYItemRenderer.readObject"));
            assertThat(callerFrame.getFileName(), equalTo("StandardXYItemRenderer.java"));
            assertThat(callerFrame.getLineNumber(), equalTo(1056));
        }
        assertThat(traces.get(0).getFrame(0).getLineNumber(), equalTo(553));
        assertThat(traces.get(0).getExceptionName(), equalTo("java.io.NotActiveException"));
        assertThat(traces.get(1).getFrame(0).getLineNumber(), equalTo(554));
        assertThat(traces.get(1).getExceptionName(), equalTo("java.io.NotActiveException2"));
    }

    @Test
    public void testSynthesizeWithMultipleStackTraces() {
        String input = "{\"org.jfree.data.xy.DefaultWindDataset.seriesNameListFromDataArray(java.lang.Object[][])-java.lang.StringBuffer.append(String)\": {\n"
                + "        \"call-site-sig\": \"org.jfree.data.xy.DefaultWindDataset.seriesNameListFromDataArray(java.lang.Object[][])\", \n"
                + "        \"exception-list\": {\n"
                + "            \"level_0\": [\n"
                + "                [\n"
                + "                    \"1960\", \n"
                + "                    \"java.lang.StringIndexOutOfBoundsException\"\n"
                + "                ], \n"
                + "                [\n"
                + "                    \"1963\", \n"
                + "                    \"java.lang.StringIndexOutOfBoundsException\"\n"
                + "                ], \n"
                + "                [\n"
                + "                    \"1967\", \n"
                + "                    \"java.lang.StringIndexOutOfBoundsException\"\n"
                + "                ]\n"
                + "            ], \n"
                + "            \"level_1\": [\n"
                + "                [\n"
                + "                    [\n"
                + "                        \"558\", \n"
                + "                        \"java.io.ObjectInputStream.defaultReadFields(Object, ObjectStreamClass)\"\n"
                + "                    ], \n"
                + "                    [\n"
                + "                        \"2264\", \n"
                + "                        \"java.lang.ClassCastException\"\n"
                + "                    ]\n"
                + "                ]\n"
                + "            ], \n"
                + "            \"level_2\": [\n"
                + "                [\n"
                + "                    [\n"
                + "                        \"270\", \n"
                + "                        \"java.lang.AbstractStringBuilder.append(String)\"\n"
                + "                    ], \n"
                + "                    [\n"
                + "                        \"449\", \n"
                + "                        \"java.lang.String.getChars(int, int, char[], int)\"\n"
                + "                    ], \n"
                + "                    [\n"
                + "                        \"818\", \n"
                + "                        \"java.lang.StringIndexOutOfBoundsException\"\n"
                + "                    ]\n"
                + "                ], \n"
                + "                [\n"
                + "                    [\n"
                + "                        \"270\", \n"
                + "                        \"java.lang.AbstractStringBuilder.append(String)\"\n"
                + "                    ], \n"
                + "                    [\n"
                + "                        \"449\", \n"
                + "                        \"java.lang.String.getChars(int, int, char[], int)\"\n"
                + "                    ], \n"
                + "                    [\n"
                + "                        \"821\", \n"
                + "                        \"java.lang.StringIndexOutOfBoundsException\"\n"
                + "                    ]\n"
                + "                ], \n"
                + "                [\n"
                + "                    [\n"
                + "                        \"270\", \n"
                + "                        \"java.lang.AbstractStringBuilder.append(String)\"\n"
                + "                    ], \n"
                + "                    [\n"
                + "                        \"449\", \n"
                + "                        \"java.lang.String.getChars(int, int, char[], int)\"\n"
                + "                    ], \n"
                + "                    [\n"
                + "                        \"824\", \n"
                + "                        \"java.lang.StringIndexOutOfBoundsException\"\n"
                + "                    ]\n"
                + "                ]\n"
                + "            ], \n"
                + "            \"id\": \"java.lang.StringBuffer.append(String)\"\n"
                + "        }, \n"
                + "        \"api-method-sig\": \"java.lang.StringBuffer.append(String)\", \n"
                + "        \"call-site-line\": \"285\", \n"
                + "        \"java-file-path\": \"DefaultWindDataset.java\"\n"
                + "    }}";
        List<StackTrace> traces = new JSONStackTraceSynthesizer().synthesize(input);
        assertThat(traces, hasSize(7));
        for (StackTrace trace : traces) {
            LOG.debug("Checking stack trace {}", trace);
            Frame jdkFrame = trace.getFrame(trace.getFramesCount() - 1);
            assertThat(trace.getFramesCount(), allOf(greaterThanOrEqualTo(1), lessThanOrEqualTo(4)));
            assertThat(jdkFrame.getMethodName(), equalTo("org.jfree.data.xy.DefaultWindDataset.seriesNameListFromDataArray"));
            assertThat(jdkFrame.getFileName(), equalTo("DefaultWindDataset.java"));
            assertThat(jdkFrame.getLineNumber(), equalTo(285));
        }
    }

    @Test
    public void testSynthesizeWithNoException() {
        String input = "{\"org.jfree.chart.renderer.xy.StandardXYItemRenderer.readObject(java.io.ObjectInputStream)-java.io.ObjectInputStream.defaultReadObject()\": {\n"
                + "        \"call-site-sig\": \"org.jfree.chart.renderer.xy.StandardXYItemRenderer.readObject(java.io.ObjectInputStream)\", \n"
                + "        \"exception-list\": {\n"
                + "            \"level_0\": [], \n"
                + "            \"level_1\": [], \n"
                + "            \"level_2\": [], \n"
                + "            \"id\": \"java.io.ObjectInputStream.defaultReadObject()\"\n"
                + "        }, \n"
                + "        \"api-method-sig\": \"java.io.ObjectInputStream.defaultReadObject()\", \n"
                + "        \"call-site-line\": \"1056\", \n"
                + "        \"java-file-path\": \"StandardXYItemRenderer.java\"\n"
                + "    }}";
        List<StackTrace> traces = new JSONStackTraceSynthesizer().synthesize(input);
        assertThat(traces, hasSize(0));
    }

}
