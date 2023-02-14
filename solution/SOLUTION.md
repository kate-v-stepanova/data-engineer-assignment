# Solution for the assignment

## Content

[Prepare virtual env](#prepare-virtual-env)

[Task 1. Parse data files](#task-1.-parse-data-files)

[Task 2]()

[Task 3. Query UniProtKB](#task-3.-query-UniProtKB)



## Prepare virtual env

### 1. Clone github repo

```
git clone git@github.com:kate-v-stepanova/data-engineer-assignment.git
cd data-engineer-assignment
```

### 2. Create conda environment

```
conda create -n assignment python=3.8
source activate assignment
pip install -r pip_requirements.txt
```

Requirements are the following:

```
pandas
sqlite3
click
```

## Task 1. Parse data files

### 0. Print script help

Get help:

```
python solution/1_parse_files.py --help
```

Will give the following output:

```
Usage: 1_parse_files.py [OPTIONS] INFILE DBFILE [TABLE_NAME] COMMAND [ARGS]...

Options:
  --replace-if-exists  replace table if exists, otherwise do nothing
  --help               Show this message and exit.

Commands:
  illumina      parse illumina data
  mic           parse mic data
  nanopore      parse nanopore data
  sample-table  parse sample_table
```



### 1. Parse `Illumina` file

```
python solution/1_parse_files.py illumina_data.tree solution/assignment_db.sql illumina illumina
```

### 2. Parse `nanopore` file

```
python solution/1_parse_files.py illumina_data.tree solution/assignment_db.sql nanopore nanopore
```

### 3. Parse `sample_table`

```
python solution/1_parse_files.py sample_table.csv solution/assignment_db.sql sample_table sample-table
```

### 4. Parse `MIC` file

```
python solution/1_parse_files.py MIC_data.csv solution/assignment_db.sql mic mic
```



## Task 2.



## Task 3. Query UniProtKB

```
python solution/3_query_protKB.py assignment_db.sql
```

## Task 4.

**1. Question:** How would you modify the data schema to make the tables "joinable"?

​	**Solution:** Adding a column `Experiment ID`  to all tables

**2. Question:** If you have been exposed to FAIR principles, how would you modify the schema to make it most compatible with other datasets available in public repositories

**Solution:**



**3. Question:** What would be your recommendation for possible tools to manage such tabular data?

**Solution:** 