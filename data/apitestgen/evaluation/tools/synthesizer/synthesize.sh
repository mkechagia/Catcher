#!/bin/bash -e

# Stack trace synthesizer exectuion script
#
# author: Xavier Devroey

if [ "$2" == "" ] ; then
    echo "Usage : $0 <subject-name> <input.json> <experiment-folder>";
    echo "Example : $0 jfreechart-1.2.0 jfree.json";
    exit 1;
fi;

scriptdir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
jarfile=$scriptdir/stacktrace-synthesizer-0.0.2-SNAPSHOT-jar-with-dependencies.jar
subject=$1
jsonfile=$2
stacktraces=$3/stacktraces

java -jar $jarfile -c $subject -i $jsonfile -o $stacktraces
