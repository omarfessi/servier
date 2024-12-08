# Servier Project

This repository contains a set of scripts and tools for aggregating and processing drug and clinical trial data using the **servier-aggregate** pipeline.

You can integrate it in your DAG workflow by using bashscripts operators and launch the scripts you will discover here

## Requirements

- Python 3.8 or later

## Installation and Setup

Follow the steps below to install and get the project up and running.
##### 1. Clone the Repository
```bash
git clone git@github.com:omarfessi/servier.git
```
##### 2. Navigate to the project directory
```bash
cd servier
```

##### 3. Initialize Submodules (to install data folder)
```bash
git submodule init
git submodule update
```

##### 4. Set Up the Virtual Environment and Install Dependencies and launch unit tests
```bash
./run.sh test:wheel-locally
```
This will:
- Create a virtual environment
- Install the dependencies from requirements-dev.txt
- Build and install the project’s wheel

##### 5. Create Data Directories
The project expects specific directories for storing data. You can create these directories by running:
```bash
./run.sh data-dir:create
```
This will create the necessary directory structure:
```bash
data/
├── corrupted_data
├── gold_zone
├── landing_zone
└── silver_zone
```
The submodule's data will be moved to data/landing_zone/.


##### 6. Run the Aggregation Pipelines
Once the directories are set up, you can run the data aggregation pipelines. Below are the available pipelines that can be executed using run.sh.

<u>Main Pipeline</u>
To run the main aggregation pipeline, use:
```bash
./run.sh servier-aggregate:main-pipeline
```
This will process the raw clinical trial data and drug data and generate aggregated results.


<u>Journal with Max Drugs</u>
To process journals with the maximum number of drugs, use:


```bash
./run.sh servier-aggregate:journal-with-max-drugs
```
<u>Get Drugs from Journals Mentioning a Specific Drug</u>
To run a pipeline that extracts drugs from journals mentioning a specific drug (e.g., TETRACYCLINE), use:
```bash
./run.sh servier-aggregate:get-drugs-from-journals-that-mention-a-specific-drug TETRACYCLINE
```


##### 7.Cleaning Data Directories
You can clean the contents of the data directories (corrupted_data, gold_zone, silver_zone) by running:
```bash
./run.sh data-dir:clean
```

##### 8. Development Mode
If you'd like to install the project in development mode (editable mode), use the following command:
```bash
./run.sh install:dev-mode
```

##### 9. Available task
```bash
./run.sh help
```

##### 10. SQL part of the test
duckddl.py and .sql files are only there to answer the second part questions of the test. They have nothing to do with the servier project being developped.
I used duckdb to use their in-memory processing and issues sql queries, if you want to try it out, activate a virtual environment and bash ```pip install duckdb```and have fun :) 