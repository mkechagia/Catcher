# Catcher

Tool that combines static exception propagation and search-based software testing to automatically detect (and generate test cases) for API misuses in Java client programs.

# Structure

The structure of the experiment folder is the following:

- `subjects/` contains the subjects for the experiments. Each subject folder contains the `.jar` files of the projects.
- `tools/` contains the tools required to run the experiment.

# Execution

## Subjects (`config.sh`)

The subjects are listed in `config.sh`. Comment a line to remove one particular subject from the evaluation. Each subject must have a corresponding folder in `subjects/` containing the `.jar` file used for the analysis.

## eRec analysis (`tools/erec/erec.sh`)

The eRec analyze is launched using `tools/erec/erec.sh`. The script receives as parameters the name of the subject. The folder with the `.jar` files for that subject and the experiment folder where to produce the `experiment/<subject-name>/erec.json` file used by the synthesizer.

- Inputs:
  - Subject name (e.g., `jfreechart-1.2.0`)
  - Folder with the `.jar` files (e.g., `subject/jfreechart-1.2.0`)
  - Experiment location where to produce intermediate files and `erec.json` file (e.g., `experiment/jfreechart-1.2.0`)
- Outputs:
  - `erec.json` file in the experiment location (e.g., `experiment/jfreechart-1.2.0/erec.json`)

## Stack traces synthesis (`tools/synthesizer/synthesize.sh`)

The stack traces synthesizer is launched using `synthesizer/synthesize.sh`. The script receives as parameters the name of the subject and the experiment folder where to find the `erec.json` file produced by eRec and produce the stack traces in `experiment/<subject-name>/stacktraces`.

- Inputs:
  - Subject name (e.g., `jfreechart-1.2.0`)
  - Experiment location where to find the `erec.json` file (e.g., `experiment/jfreechart-1.2.0`)
- Outputs:
  - Stack traces (`.log` files) in `experiment/<subject-name>/stacktraces` (e.g., `experiment/jfreechart-1.2.0/stacktraces`)
  - `<subject-name>.json` file in `experiment/<subject-name>/stacktraces` (e.g., `experiment/jfreechart-1.2.0/stacktraces/jfreechart-1.2.0.json`)

## EvoSuite analysis (`tools/evosuite/launcher-1.0.sh`)

See the guidelines document for the setting of the parameters and how to launch the tool.

# Synthesizing stack traces for a new project

1. In `config.sh`, comment/uncomment the lines of the projects for which you want to synthesize stack traces. Add a line for each new project (the name should be the name used in `experiment/`).

2. Execute `. runsynthesizer.sh`.

# Tutorial on VM

See catcher-artifact.pdf

# Run on VM

https://drive.google.com/open?id=1sqms5pGyAlYFaSzuWRSE0bxscsQEW6xP

# Download data set

https://drive.google.com/open?id=1luIkAC6q9HPhlbdvy_Y8JTKgPnp4cUVi
