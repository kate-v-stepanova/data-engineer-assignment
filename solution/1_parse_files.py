import click
import pandas as pd
import sqlite3
import yaml

import sys
import os

@click.group()
@click.option('--replace-if-exists', default=False, help='replace table if exists, otherwise do nothing')
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
    df = pd.read_csv(infile, names=['tree'], engine='python', error_bad_lines=False)

    # remove *trimming_report.txt files
    df = df.loc[~df['tree'].str.endswith('.txt')]

    # remove slurm reports
    df = df.loc[~df['tree'].str.endswith('trimSlurmReports')]
    df = df.loc[~df['tree'].str.endswith('.out')]

    # get level in a tree for each file
    df['level'] = df['tree'].str.count(' ')
    df['tree'] = df['tree'].str.split(' ').str[-1]

    # path for the level 1: dirname (line 0) + filename
    df['full_path'] = df['tree'][0] + '/'
    df.loc[df['level'] == 1, 'full_path'] = df.loc[df['level'] == 1, 'full_path'] + df.loc[df['level'] == 1, 'tree']
    df = df.drop(0) # we don't need it anymore

    # for the level 2: 
    # we know, there is just 1 subdir
    subdir = df.loc[(df['level'] == 1) & (~df['tree'].str.endswith('.gz'))]
    # files in this subdir
    level2 = df.loc[df['level'] == 2]
    df.loc[df['level'] == 2, 'full_path'] = subdir['full_path'].iloc[0] + '/' + level2['tree']
    # remove subdir rows
    df = df.drop(subdir.index)
   
    import pdb; pdb.set_trace()
    df['experiment'] = df['tree'].str.split('_S').str[0]
    df['sample'] = df['tree'].str.split('_S').str[-1].str.split('_L').str[0]

    # get files with R1 and R2
    read1 = df.loc[df['tree'].str.contains('_R1_')].drop(['tree', 'level'], axis=1)
    read2 = df.loc[df['tree'].str.contains('_R2_')].drop(['tree', 'level'], axis=1)

    import pdb; pdb.set_trace()
    df = read1.merge(read2, on=['experiment', 'sample'])
    df.columns = ['read1', 'experiment', 'sample', 'read2']
    df = df[['experiment', 'sample', 'read1', 'read2']]
    df = df.drop('experiment', axis=1)

    # write sql
    col_types = ['integer', 'text', 'text']
    df.to_sql(table_name, conn, dtypes=col_types)
    conn.close()
    print('Data from {} has been saved into DB: {}.{}'.format(infile, dbfile, table_name))

    

@cli.command()
@click.pass_context
def nanopore(ctx):
    """
    parse nanopore data
    """
    pass

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
    df.to_sql(table_name, conn, if_exists=if_exists, dtype=dict_types)

    # close connection
    conn.close()

    print('Data from {} has been saved into a DB: {}.table_name'.format(infile, dbfile, table_name))


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
    df.to_sql(table_name, conn, if_exists=if_exists, dtype=dict_types)
    # close connection
    conn.close()

    print('Data from {} has been saved into a DB: {}.{}'.format(infile, dbfile, table_name))



if __name__ == '__main__':
    cli(obj={})
