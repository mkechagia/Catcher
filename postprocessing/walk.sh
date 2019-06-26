#!/bin/bash

#name  : Maria Kechagia
#email : m.kechagia@tudelft.nl
#date  : Jan 2019

# Directory of the experiment_all folder
cwd=`pwd`

cd $cwd

echo "Processing of the results.\n"

find . -name "coverageResults.csv" > list.txt

python2.7 /home/guest/Documents/postprocessing/processing_results.py $cwd/list.txt
