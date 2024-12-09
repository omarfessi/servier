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
##### 10. Potentials improvements to scale up and handle large data.
*Issues with Current Approach*:
<u>Memory Usage</u>: If the dataset is very large, storing all data in memory might lead to memory exhaustion.
<u>Inefficiency</u>: The function reads the file row-by-row and performs validation on each row. For very large datasets, this can be extremely slow.
<u>Single-threaded Processing</u>: which limits the speed of execution.

For large datasets, it's better to use a framework that allows for batch processing, parallelization, and efficient memory management. Here's some examples:
1. Use a Distributed Framework like Spark to enable parallel processing and keep python-like logic to overcome the potentiel issues with the current approach. User Defined Functions can be of use to validate and clean data instead.
Here's a example of UDF that can check if the title is not empty
```python
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

# UDF to check for empty strings
def check_not_empty(value: str) -> str:
    if not value or value.strip() == "":
        return "Invalid title"
    return value

# Register UDF in Spark
check_not_empty_udf = udf(check_not_empty, StringType())

# Apply UDF to the DataFrame
pubclinical_df = pubclinical_df.withColumn("validated_title", check_not_empty_udf(pubclinical_df["title"]))
```


2. Use SQL within a Cloud datawarehouse  to take advantage of their distributed processing engine like Bigquery or Snowflake. DBT or Dataform for data transformation (to achieve the final results in silver and gold zones) and Great Expectation to validate data and set up rules(instead of Pydantic)

3. Use best suited table/file schemas.
Using different file format like Apache Parquet can be significantly better than using CSV or JSON when dealing with large datasets, especially in a distributed data processing environment like Apache Spark.
Parquet is a columnar storage format(which means it stores data by columns rather than rows) it allows for better performance especially if only a tiny subset of columns are needed like  **title** or **drug**, the processing framework would only read those 2 columns instead of the whole row which reduces mem usage.
Parquet can as well use efficient compression algorithms that helps reduce storage space.
In addition to high performance capabilities of Parquet, it is interoperable and typed schema to ensure data is consistent.
The same for Bigquery since it uses **columnar storage** format (compared to csv or json). With Bigquery it is possible to **partition** data by date column and only query the partition we are intrested in. To go even further with **clustering** and organize data within each partition by one or more columns to make query even faster and efficient.
This is an example of creating a table that hold clinical trials data, it is paritionned by date and clustering by journal, drug
```SQL
CREATE OR REPLACE TABLE `project-id.dataset-id.clinical_trials`
PARTITION BY date
CLUSTER BY journal, drug

```

##### 11. SQL part of the test
duckddl.py and .sql files are only there to answer the second part questions of the test. They have nothing to do with the servier project being developped.
I used duckdb to use their in-memory processing and issues sql queries, if you want to try it out, activate a virtual environment and bash ```pip install duckdb```and have fun :)
