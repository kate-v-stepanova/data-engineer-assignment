import click
import pandas as pd
import sqlite3

import sys
import os

@click.group()
@click.option('--replace-if-exists', default=False, help='replace table if exists, otherwise do nothing')
@click.argument('infile')
@click.argument('dbfile')
@click.argument('table_name', required=False) # optional
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
    pass

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

    print('Data from {} has been saved into a DB: {}'.format(infile, dbfile))


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

    print('Data from {} has been saved into a DB: {}'.format(infile, dbfile))



if __name__ == '__main__':
    cli(obj={})
