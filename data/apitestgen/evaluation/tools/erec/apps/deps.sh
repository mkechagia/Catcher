#/bin/bash

#author      : m.kechagia@tudelft.nl
#last update : 21-7-2018

cwd=$1

# Create a jar file with all dependencies.
# (Only if there are jar files with different names from the project.)
for F in `ls *jar`
do
    otherjar=`echo "$F"`
    fname=`echo "$1.jar"`
    if [ "$fname" != "$otherjar" ];
    then
	# move deps in jars folder and create .jar file with deps
        jar tvf *.jar
        ls | xargs -I {} jar xvf  {}
        mkdir jars
        mv *.jar jars
        jar cvf $1.jar .
        jar tvf $1.jar
        break
    else
		echo "File "$fname" with the dependencies is already created."
	fi
done

# Clean useless folders and files.
for FILE in `ls -l`
do
	if test -d $FILE
	then
    	fname=`echo $FILE`
		if [ $fname != "jars" ] && [ $fname != `echo $1` ];
		then
	    	rm -r -f $FILE
		fi
    elif test -f $FILE
	then
		fname=`echo $FILE`
		if [ $fname != `echo $1.jar` ];
		then
	    	rm $FILE
		fi
	fi
done

# Create a subfolder for the project in the experiment folder
cd ../../experiment
count=`find . -type d -name $1 | wc -l`
if [ $count == 0 ];
then
	mkdir $1
fi

cd ../subjects/$1
