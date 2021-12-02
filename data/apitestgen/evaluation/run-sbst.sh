#!/bin/bash -e

# Runs the experiment for a given subject

#source config.sh

if [ "$1" == "" ] ; then
    echo "Usage : $0 <subject-name>";
    echo "Exemple : $0 commons-lang-2.3-SNAPSHOT";
    echo "Subjects are:"
    for s in ${SUBJECTS[*]}; do echo $s; done;
fi;

scriptdir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

subject=$1
jarfolder=$scriptdir/subjects/$subject 
expefolder=$scriptdir/experiment/$subject 
jsonfile=$scriptdir/experiment/$subject/erec.json

# Run extended EvoSuite

java -jar tools/evosuite/launcher-1.0.jar . 1000 1 1 catchy_fast xwiki-commons-text-13.10