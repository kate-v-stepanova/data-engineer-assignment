# Solution for the assignment

## Content

0. [Set up virtual env](#set-up-virtual-env)
1. [Parse data files](#parse-data-files)

## Set up virtual env

### 1. Create conda environment

```
conda create -n scicore python=3.8
source activate scicore
pip install -r pip_requirements.txt
```

## Parse data files

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

