#!/bin/bash -e

# Runs the experiment for a given subject

source config.sh

scriptdir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# Running eRec on all subjects
for s in ${SUBJECTS[*]}; do
        subject=$s
        jarfolder=$scriptdir/subjects/$subject 
        expefolder=$scriptdir/experiment/$subject 
        # Run eRec
        (. $scriptdir/tools/erec/erec.sh $subject $jarfolder $expefolder)
done;

# Running synthesizer on all subjects 
for s in ${SUBJECTS[*]}; do
        subject=$s
        expefolder=$scriptdir/experiment/$subject 
        jsonfile=$scriptdir/experiment/$subject/erec.json
        # Run synthesizer
        (. $scriptdir/tools/synthesizer/synthesize.sh $subject $jsonfile $expefolder)
done;

for s in ${SUBJECTS[*]}; do
        subject=$s
        # Run EvoSuite
        (cd $scriptdir && java -jar tools/evosuite/launcher-1.0.jar . 1000 1 1 catchy_fast $subject)
done;