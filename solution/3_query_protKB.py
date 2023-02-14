import pandas as pd
import sqlite3

import json
import requests
import io
import sys

dbfile = sys.argv[1]

table_name = 'UniProtKB'
if len(sys.argv) > 2:
    table_name = sys.argv[2]

requestURL = 'https://rest.uniprot.org/uniprotkb/search?query=taxonomy_id:573+AND+imipenem&format=tsv'
r = requests.get(requestURL, headers={ "Accept" : "application/json"})

if not r.ok:
  r.raise_for_status()
  sys.exit()


df = pd.read_csv(io.StringIO(r.text), sep='\t')

# open dbfile
try:
    conn = sqlite3.connect(dbfile)
except:
    print('Cant open connection: {}'.format(dbfile))
    sys.exit()

col_types = ['text', 'text', 'text', 'text', 'text', 'text', 'text', 'integer']
dict_types = {df.columns[i]: col_types[i] for i in range(len(df.columns))}
try:
    df.to_sql(table_name, conn, dtype=dict_types, index=False, if_exists='replace')
except:
    print('Cant write table {} into {}'.format(table_name, dbfile))
    sys.exit()

conn.close()
print('Table has been updated: {} in {}'.format(table_name, dbfile))
