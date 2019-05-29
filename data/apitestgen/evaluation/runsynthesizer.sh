#!/bin/bash -e

# Runs the experiment for a given subject

source config.sh

scriptdir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# Running synthesizer on all subjects 
for s in ${SUBJECTS[*]}; do
	subject=$s
	expefolder=$scriptdir/experiment/$subject 
	jsonfile=$scriptdir/experiment/$subject/erec.json
	# Run synthesizer
	(. $scriptdir/tools/synthesizer/synthesize.sh $subject $jsonfile $expefolder)
done;
