#!/bin/bash

JAVA_CLASSPATH="\
../../tools/erec/soot-material/soot-trunk.jar:\
../../tools/erec/soot-material/AXMLPrinter2.jar:\
../../tools/erec/soot-material/baksmali-2.0.3.jar:\
$JAVA_HOME/jre/lib/rt.jar:\
$JAVA_HOME/jre/lib/jsse.jar:\
$JAVA_HOME/jre/lib/jce.jar:\
"

JAR_FILE=$1
SOOT_OUT_DIR=$2
OWNCLASSPATH=$3

PROCESS_THIS="-pp -process-dir $JAR_FILE"
SOOT_CLASSPATH="\
../../tools/erec/soot-material/soot-trunk.jar:\
../../tools/erec/soot-material/AXMLPrinter2.jar:\
../../tools/erec/soot-material/baksmali-2.0.3.jar:\
$JAVA_HOME/jre/lib/rt.jar:\
$JAVA_HOME/jre/lib/jsse.jar:\
$JAVA_HOME/jre/lib/jce.jar:\
"${JAR_FILE}":\
"${OWNCLASSPATH}"\
"

SOOT_CMD="soot.Main --soot-classpath $SOOT_CLASSPATH \
 -d $SOOT_OUT_DIR\
 -allow-phantom-refs\
 -keep-line-number\
 -i org.dom4j\
 -print-tags\
 -f J\
 -i java.\
 $PROCESS_THIS
"
# You can instruct Soot to analyze more 3rd-party libraries
# by using the -include XX or -i XX command above;
# where XX is the 3rd-party library to be analyzed
# -i java\
# -include org.apache.\
# -include org.w3c. \
# -i org.dom4j \

#-show-exception-dests \
#-java-version 8\
#-include-all\
#-p cg all-reachable:true\
#-p jb use-original-names:true\
#-p cg jdkver:8\

# to increase JVM memory
java \
 -Xss50m \
 -Xmx1500m \
 -classpath  ${JAVA_CLASSPATH} \
 ${SOOT_CMD} \
 > $SOOT_OUT_DIR/soot_log.txt
