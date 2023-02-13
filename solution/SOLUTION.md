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
  --replace-if-exists BOOLEAN  replace table if already exists, otherwise do
                               nothing
  --help                       Show this message and exit.

Commands:
  illumina      parse illumina data
  mic           parse mic data
  nanopore      parse nanopore data
  sample-table  parse sample_table
```



### 1. Parse `Illumina` file

```
python solution/1_parse_files.py <illumina-file> illumina <outfile>
```

### 2. Parse `nanopore` file



### 3. Parse `sample_table`



### 4. Parse `MIC` file



## Task 2.



## Task 3. Query UniProtKB

```
python solution/3_query_protKB.py assignment_db.sql
```



## Task 4.