#!/bin/bash

#author    : m.kechagia@tudelft.nl
#las update: 21-7-2018

# Directory of the apitestgen folder
cwd=`pwd`

# make scripts executable (on macos and linux)
chmod +x $cwd/evaluation/tools/erec/apps/run-soot-jar.sh
chmod +x $cwd/evaluation/tools/erec/apps/runSootOnJar.sh
chmod +x $cwd/evaluation/tools/erec/apps/deps.sh

### APPS ###

cd $cwd/evaluation/subjects/

echo "Here, the static analysis of the projects starts.\n"

for FILE in `ls -l`
do
    if test -d $FILE
    then
        echo "$FILE is a subdirectory..."

	fname=`echo "$FILE"`
	if [ $fname == "xwiki-commons-text-13.10" ];
	then
		echo "$FILE is a subdirectory..."

		cd $FILE

		if [ -e "$cwd/evaluation/experiment/$FILE/erec.json" ]; then
			#rm "$cwd/evaluation/experiment/$FILE/erec.json"
			echo "Json file found.\n"
	    	cd ..

    		continue
 		else

 			echo "Json doesn't exist. The analysis starts."

			#create .jar with dependencies
			$cwd/evaluation/tools/erec/apps/deps.sh $FILE

			#run soot to get .jimple files
			$cwd/evaluation/tools/erec/apps/run-soot-jar.sh

			python3 $cwd/evaluation/tools/erec/api/jdk_call_graph.py $cwd/evaluation/subjects/$FILE/$FILE/ $cwd/evaluation/experiment/$FILE/ 8 java #>> progress.log 2>>progress.err &

	        # create the exceptions hierarchy from the JDK for a particular project
	        python3 $cwd/evaluation/tools/erec/api/exceptions_hierarchy.py $cwd/evaluation/subjects/$FILE/ $cwd/evaluation/experiment/$FILE/ 8 java #>> progress.log 2>>progress.err &

		# traverse and refine the might thrown exceptions of the nodes in the JDK
	        python3 $cwd/evaluation/tools/erec/api/proj_exceptions_level_2_api.py $cwd/evaluation/subjects/$FILE/ $cwd/evaluation/experiment/$FILE/ 8 java #>> progress.log 2>>progress.err &

		python3 $cwd/evaluation/tools/erec/apps/proj_exceptions_app.py $cwd/evaluation/subjects/$FILE $cwd/evaluation/experiment/$FILE/ $cwd/evaluation/experiment/$FILE/ 8 java

		echo "\n"

		cd ..

 		fi
	fi

    fi
done
