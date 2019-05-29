#!/bin/bash

#author      : m.kechagia@tudelft.nl
#last update : 21-7-2018

sampledir=`pwd`
samplepath=../../tools/erec/apps/runSootOnJar.sh

count=`find $sampledir -type f -name \java.*.jimple | wc -l`
if [ $count != 0 ];
then
	echo "Soot has arleady run in $sampledir."
else
	find $sampledir -type f -name \*.jar -maxdepth 1 -mindepth 1 |
	while read jar; do
	  name=$(basename $jar .jar)
	  mkdir -p $name
	  $samplepath $jar $name 2>$name/errors.txt
	done
fi
