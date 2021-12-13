#!/bin/bash

for SUBJECT in `ls -d */`:
do
  cd $cwd/evaluation/subjects/$SUBJECT
  
  # 1. check if there's a source file
  if ! test -d src/
  then
    echo "Missing source folder"
    exit 1;
  fi

  # 2. check for pom.xml file, if not, throw error and exit -> no build file
  if ! test -f pom.xml
  then
    echo "Missing build file pom.xml"
    exit 1;
  fi
done