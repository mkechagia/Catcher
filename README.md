# Improvements to Catcher

We have made necessary changes to create a new version of Catcher that would

These changes are:
1. Upgrade Catcher from Python 2.7 to Python3.
2. Make Catcher extendable for other subjects.
3. Create a format for running Catcher on subjects.

## Requirements
1. Make sure to have Python 3 installed.
  - Check by running `python3 --version`
2. Have the Maven command line (mvn) installed. 
  - Check by running `mvn --version`

# Structure

The structure of the experiment folder is the following:

- `subjects/` contains the subjects for the experiments. Each subject folder contains the source files of the projects.
- `tools/` contains the tools required to run the experiment.

## Instructions
1. Create a virtual environment by running `python3 -m venv <path-to-virtual-environment>` 
2. Install necessary Python dependencies by `pip3 install -r requirements.txt`
3. Create a folder with the name of your subject into the folder `data/apitestgen/evaluation/subjects/` and copy your subject code into it, making sure it contains src/, and build file names `pom.xml`
  - The name to the folder created will be used when running the analysis
4. Go to the directory by running `cd data/apitestgen`
5. Run Catcher using `bash evaluation/thrower-one-project.sh <SUBJECT-NAME>`
  - where:
    - SUBJECT-NAME is the name of the folder created inside `subjects`


Tool that combines static exception propagation and search-based software testing to automatically detect (and generate test cases) for API misuses in Java client programs.

# Evaluation Replication Instructions

We chose to evaluate Catcher using an empirical approach. This consisted of cross-checking reported misuses with the source code of the selected projects. To replicate our results, we have included the following files for your viewing:

1.	The files that contain the identified misuses for the subjects of our study are provided in data/apitestgen/evaluation/experiment. The erec.json file for each subject contains the misuses reported by Catcher. 
2.	We have also included the source code for each subject in the following google drive link: https://drive.google.com/drive/folders/1LDNm7gAlGfixrH02n0sUXLczfA0BRzLE?usp=sharing

# Execution

## Subjects (`config.sh`)

The subjects are listed in `config.sh`. Comment a line to remove one particular subject from the evaluation. Each subject must have a corresponding folder in `subjects/` containing the `.jar` file used for the analysis.


# Tutorial on VM for Catcher's original version

See catcher-artifact.pdf

# Run on VM from Catcher original version

https://drive.google.com/file/d/1UuyJTOac9kmzIUNFvFwITFwRConfUPG3/view?usp=sharing

# Subjects

https://drive.google.com/open?id=1luIkAC6q9HPhlbdvy_Y8JTKgPnp4cUVi

# Main findings from Catcher original version

https://drive.google.com/file/d/1GbiggiqCq0sha7OmiZmD3NuJuguPITFZ/view?usp=sharing

# Publication

Kechagia M., Devroey X., Panichella A., Gousios G., van Deursen A (2019). Effective and Efficient API Misuse Detection via Exception Propagation and Search-based Testing. In 2019 ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA 2019). Beijing, China: ACM.

Pre-print
https://pure.tudelft.nl/portal/files/54238155/catcher.pdf
