#!/bin/bash
#author: ataupill@ualberta.ca

cwd=`pwd`
subject=$1
# if no source folder is located and only class files located
flag=$2

if [ "$1" == "" ] ; then
  echo "Usage : $0 <subject-name> <flag>";
  echo "Example : $0 xwiki-commons-text-10.6";
  echo "Or: $0 xwiki-commons-text-10.6 false"
fi

### APPS ###

cd $cwd/evaluation/subjects/$subject

if [ "$flag" == "" ]; then
  # 1. check if there's a source file
  if ! test -d src/
  then
    echo "$subject is missing source folder"
    exit 1;
  fi
fi

# 2. check for pom.xml file, if not, throw error and exit -> no build file
if ! test -f pom.xml
then
  echo "Missing build file pom.xml"
  exit 1;
fi

if [ "$flag" != "" ]; then
  if ! test -d $cwd/evaluation/databases/$subject
  then
    echo "Codeql database for $subject missing"
    echo "Need source code in order to create one and leave flag empty"
    exit 1;
  fi
else
  # 3. create codeql database
  echo "Creating a codeql database..."
  mkdir -p $cwd/evaluation/databases
  codeql database create $cwd/evaluation/databases/$subject --overwrite --language=java
fi

# 4. compile first
echo "Compiling the project..."
mvn compiler:compile

# 5. get info from target/classes folder to the $subject folder
echo "Moving java class files in current directory"
mv target/classes/* .

# 6. delete target folder and src folder
echo "Delete target folder and src folder"
rm -rf target/
rm -rf src/

# 7. download all the dependencies
echo "Download Jar dependencies"
mvn dependency:copy-dependencies -DoutputDirectory=. -DexcludeTransitive=true -DincludeScope=compile

# 8. Run run-erec.sh from evaluation
echo "----------------------------------------------------"
echo "Running Catcher evaluation..."
cd $cwd
bash evaluation/run-erec.sh $subject