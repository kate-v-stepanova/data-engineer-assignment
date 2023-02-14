import click
import pandas as pd
import sqlite3
import yaml

import sys
import os

@click.group()
@click.option('--replace-if-exists', is_flag=True, default=False, help='replace table if exists, otherwise do nothing')
@click.argument('infile')
@click.argument('dbfile')
@click.argument('table_name', required=False, default=None) # optional
@click.pass_context
def cli(ctx, infile, dbfile, table_name, replace_if_exists):
    ctx.obj['infile'] = infile
    ctx.obj['dbfile'] = dbfile
    ctx.obj['table_name'] = table_name

    # flag to replace table if already exists -> default = fail
    if_exists = 'fail'
    if replace_if_exists == True:
        if_exists = 'replace'
    ctx.obj['if_exists'] = if_exists
 
# parse illumina data
@cli.command()
@click.pass_context
def illumina(ctx):
    """
    parse illumina data
    """
    infile = ctx.obj.get('infile')
    dbfile = ctx.obj.get('dbfile')
    table_name = ctx.obj.get('table_name') or 'illumina'
    if_exists = ctx.obj.get('if_exists')
    df = pd.read_csv(infile, names=['file'], engine='python', error_bad_lines=False)

    # remove *trimming_report.txt files
    df = df.loc[~df['file'].str.endswith('.txt')]

    # remove slurm reports
    df = df.loc[~df['file'].str.endswith('trimSlurmReports')]
    df = df.loc[~df['file'].str.endswith('.out')]

    # get level in a file for each file
    df['level'] = df['file'].str.count(' ')
    df['file'] = df['file'].str.split(' ').str[-1]

    # path for the level 1: dirname (line 0) + filename
    df['full_path'] = df['file'][0] + '/'
    df.loc[df['level'] == 1, 'full_path'] = df.loc[df['level'] == 1, 'full_path'] + df.loc[df['level'] == 1, 'file']
    df = df.drop(0) # we don't need it anymore

    # for the level 2: 
    # get subdir (there is just one)
    subdir = df.loc[(df['level'] == 1) & (~df['file'].str.endswith('.gz'))]

    # get files in this subdir
    level2 = df.loc[df['level'] == 2]

    # add full path
    df.loc[df['level'] == 2, 'full_path'] = subdir['full_path'].iloc[0] + '/' + level2['file']

    # remove subdir rows
    df = df.drop(subdir.index)

    # get experiment ID and sample ID (we need experiment ID to merge rows)   
    df['experiment'] = df['file'].str.split('_S').str[0]
    df['sample'] = df['file'].str.split('_S').str[-1].str.split('_L').str[0]

    # get R1 and R2
    read1 = df.loc[df['file'].str.contains('_R1_')].drop(['file', 'level'], axis=1)
    read2 = df.loc[df['file'].str.contains('_R2_')].drop(['file', 'level'], axis=1)

    # merge into one table
    df = read1.merge(read2, on=['experiment', 'sample'])

    # re-arrange cols
    df.columns = ['read1', 'experiment', 'sample', 'read2']
    df = df[['experiment', 'sample', 'read1', 'read2']]
    df = df.drop('experiment', axis=1)

    # open / create database file
    conn = sqlite3.connect(dbfile)

    # write sql
    col_types = ['integer', 'text', 'text']
    dict_types = {df.columns[i]: col_types[i] for i in range(len(df.columns))}
    df.to_sql(table_name, conn, dtype=dict_types, if_exists=if_exists, index=False)
    conn.close()
    print('Data from {} has been saved into DB: {}.{}'.format(infile, dbfile, table_name))
    

@cli.command()
@click.pass_context
def nanopore(ctx):
    """
    parse nanopore data
    """
    infile = ctx.obj.get('infile')
    dbfile = ctx.obj.get('dbfile')
    table_name = ctx.obj.get('table_name') or 'nanopore'
    if_exists = ctx.obj.get('if_exists')
    df = pd.read_csv(infile, names=['file'], engine='python', error_bad_lines=False)

    # get level
    df['level'] = df['file'].str.count(' ')

    # trim string - take everything after space
    df['file'] = df['file'].str.split(' ').str[-1]

    # get 0-level (directories)
    level0 = df.loc[df['level'] == 0].copy()

    # get start and end index for the files in each directory
    level0['start'] = level0.index
    level0['end'] = level0.index.tolist()[1:] + [len(df)-1]

    # 
    for i, row in level0.iterrows():
        seq_date =  row['file'].split('/')[1].split('_')[0]
        df.loc[row['start']:row['end'], 'sequenced'] = seq_date
        df.loc[row['start']:row['end'], 'full_path'] = row['file'] + '/' + df.loc[row['start']:row['end'], 'file']
        
    # remove dir rows 
    df = df.drop(level0.index)

    # re-arrange cols
    df = df[['sequenced', 'full_path']]

    # open / create database file
    conn = sqlite3.connect(dbfile)

    # save to sql
    col_types = ['text', 'date']
    dict_types = {df.columns[i]: col_types[i] for i in range(len(df.columns))}
    df.to_sql(table_name, conn, dtype=dict_types, if_exists=if_exists, index=False)
    conn.close()
    print('Data from {} has been saved into DB: {}.{}'.format(infile, dbfile, table_name))


# parse sample table
@cli.command()
@click.pass_context
def sample_table(ctx):
    """
    parse sample_table
    """
    infile = ctx.obj.get('infile')
    dbfile = ctx.obj.get('dbfile')
    if_exists = ctx.obj.get('if_exists')

    # if None -> sample_table
    table_name = ctx.obj.get('table_name') or 'sample_table'
  
    # read input file
    df = pd.read_csv(infile, na_filter=False)

    # open / create database file
    # TODO: add try-except
    conn = sqlite3.connect(dbfile)

    # specify sql type for each col
    col_types = ['integer', 'integer', 'text', 'text', 'integer', 'integer', 'text', 'real', 'integer', 'integer', 'integer', 'integer', 'integer']
    dict_types = {df.columns[i]: col_types[i] for i in range(len(df.columns))}

    # save df to sql
    df.to_sql(table_name, conn, if_exists=if_exists, dtype=dict_types, index=False)

    # close connection
    conn.close()

    print('Data from {} has been saved into a DB: {}: {}'.format(infile, dbfile, table_name))


# parse mic data
@cli.command()
@click.pass_context
def mic(ctx):
    """
    parse mic data
    """
    infile = ctx.obj.get('infile')
    dbfile = ctx.obj.get('dbfile')
    if_exists = ctx.obj.get('if_exists')

    # if None -> MIC
    table_name = ctx.obj.get('table_name') or 'MIC'
  
    # read input file
    df = pd.read_csv(infile, na_filter=False)
    # open / create database file
    # TODO: add try-except
    conn = sqlite3.connect(dbfile)

    # specify sql type for each col
    col_types = ['text', 'integer', 'text', 'text', 'integer', 'integer', 'text', 'real', 'DATE', 'text', 'text', 'text', 'text', 'text', 'text', 'text', 'text', 'text', 'text', 'text', 'text', 'text', 'text', 'text', 'text', 'text', 'text', 'text', 'text', 'text', 'text', 'text', 'text', 'text',  'text', 'text', 'text', 'text',  'text', 'text', 'text', 'text', 'text', 'text', 'text']
    dict_types = {df.columns[i]: col_types[i] for i in range(len(df.columns))}

    # save df to sql
    df.to_sql(table_name, conn, if_exists=if_exists, dtype=dict_types, index=False)
    # close connection
    conn.close()

    print('Data from {} has been saved into a DB: {}.{}'.format(infile, dbfile, table_name))


if __name__ == '__main__':
    cli(obj={})
