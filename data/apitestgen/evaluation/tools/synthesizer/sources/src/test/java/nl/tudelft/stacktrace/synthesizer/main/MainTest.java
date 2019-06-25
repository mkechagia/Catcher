package nl.tudelft.stacktrace.synthesizer.main;

import com.google.common.collect.Lists;
import java.io.File;
import java.util.List;
import org.junit.Test;
import static org.junit.Assert.*;
import static org.hamcrest.Matchers.*;
import org.junit.Rule;
import org.junit.rules.TemporaryFolder;
import org.junit.rules.TestRule;
import org.junit.rules.TestWatcher;
import org.junit.runner.Description;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 *
 * @author Xavier Devroey - xavier.devroey@gmail.com
 */
public class MainTest {

    private static final Logger LOG = LoggerFactory.getLogger(MainTest.class);

    @Rule
    public TestRule watcher = new TestWatcher() {
        @Override
        protected void starting(Description description) {
            LOG.info(String.format("Starting test: %s()...",
                    description.getMethodName()));
        }
    ;
    };
    
    @Rule
    public TemporaryFolder folder = new TemporaryFolder();

    public MainTest() {
    }

    @Test
    public void testMain() throws Exception {
        String i = "src" + File.separator + "test" + File.separator + "resources" + File.separator + "commons-lang3-3.7-simple.json";
        String o = folder.newFolder().getAbsolutePath();
        String c = "testcase";
        Main.main(new String[]{"-i", i, "-o", o, "-c", c});
        File outputFolder = new File(o);
        List<String> content = Lists.newArrayList();
        for(File f: outputFolder.listFiles()){
            content.add(f.getName());
        }
        assertThat(content, hasSize(3));
        assertThat(content, containsInAnyOrder("StandardXYItemRenderer", "DefaultWindDataset", "testcase.json"));
    }

}
