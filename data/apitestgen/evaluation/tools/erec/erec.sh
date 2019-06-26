#!/bin/bash -e

# eRec tool execution script for one subject
if [ "$3" == "" ] ; then
    echo "Usage : $0 <subject-name> <subject-folder> <experiment-folder>";
    echo "Example : $0 jfreechart-1.2.0 subject/jfreechart-1.2.0 experiment/jfreechart-1.2.0 ";
    exit 1;
fi;

scriptdir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
subject=$1
jars=$2
experiment=$3

. $scriptdir/run-apps-analysis-one-project.sh # use run-apps-analysis-all.sh for all projects

echo "Script in directory $scriptdir"
echo "Subject name $subject"
echo "Jar files in $jars"
echo "Experiment in directory $experiment"
