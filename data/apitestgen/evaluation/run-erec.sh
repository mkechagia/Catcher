#!/bin/bash -e

# Runs the experiment for a given subject

source config.sh

if [ "$1" == "" ] ; then
    echo "Usage : $0 <subject-name>";
    echo "Exemple : $0 commons-lang-2.3-SNAPSHOT";
    echo "Subjects are:"
    for s in ${SUBJECTS[*]}; do echo $s; done;
    echo "Missing subject name!!!"
    exit 1
fi;

scriptdir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

subject=$1
jarfolder=$scriptdir/subjects/$subject 
expefolder=$scriptdir/experiment/$subject 
# jsonfile=$scriptdir/experiment/$subject/erec.json

# Run eRec
. $scriptdir/tools/erec/erec.sh $subject $jarfolder $expefolder
# . $scriptdir/tools/erec/erec.sh xwiki-commons-text-10.6 evaluation/subjects/xwiki-commons-text-10.6 evaluation/experiment/xwiki-commons-text-10.6