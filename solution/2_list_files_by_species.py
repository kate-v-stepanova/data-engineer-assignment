import pandas as pd
import sqlite3

import sys

dbfile = sys.argv[1]
species = sys.argv[2]
outfile = sys.argv[3]

def query_db(conn, query, table):
    try:
        cur = conn.execute(query)
    except:
        print('Cant fetch data from table: {}'.format(table))
        sys.exit()
    data = cur.fetchall()
    cols = [d[0] for d in cur.description]
    df = pd.DataFrame(data, columns=cols)
    return df

# connect to DB
try: 
    conn = sqlite3.connect(dbfile)
except:
    print('Cant connect to DB: {}'.format(dbfile))
    sys.exit()

# Get data from sample_table 
query = 'SELECT * from sample_table where Species = "{}"'.format(species)
df = query_db(conn, query, 'sample_table')

if len(df) == 0:
    print('No entries found for species: {}'.format(species))
    sys.exit()

# get illumina identifiers
labor_nrs = df['Labor Number'].tolist()

# Get data from illumina table
## Yeah - querying the WHOLE table
query2 = 'SELECT * FROM illumina'
df2 = query_db(conn, query2, 'illumina')

# Extract Labor Number from file path (assuming both R1 and R2 have the same Nr.)
df2['Labor Number'] = df2['read1'].str.split('/').str[-1].str.split('-').str[0]

# Get data from nanopore table
seq_dates = df['sequenced'].astype(str).unique().tolist() + df['resequenced'].astype(str).unique().tolist()
query3 = 'SELECT * from nanopore WHERE sequenced IN ("{}")'.format('","'.join(seq_dates))
df3 = query_db(conn, query3, 'nanopore')
df3['sequenced'] = df3['sequenced'].astype(int)
df3['barcode'] = df3['full_path'].str.split('/').str[-1].str.replace('.fastq.gz', '').str.replace('BC', '')

df['barcode'] = df['barcode'].astype(str)

# get illumina files
illumina_files = df.merge(df2, on='Labor Number')
seq_files = df.merge(df3)

# get nanopore files
re_df = df.loc[df['resequenced'] != '']
re_df['sequenced'] = re_df['resequenced'].astype(int)
re_df['barcode'] = re_df['rebarcode'].astype(str)
reseq_files = re_df.merge(df3)


# Add R1 files
all_files = pd.DataFrame()
all_files['path'] = illumina_files['read1']
all_files['subset'] = 'R1'

# Add R2 files
r2 = pd.DataFrame()
r2['path'] = illumina_files['read2']
all_files = all_files.append(r2, ignore_index=True)
all_files.loc[all_files['subset'].isna(), 'subset'] = 'R2'
all_files['source'] = 'Illumina'

# Add seq files
seq = seq_files[['full_path']]
seq.columns = ['path']
all_files = all_files.append(seq, ignore_index=True)
all_files.loc[all_files['subset'].isna(), 'subset'] = 'seq'

# Add reseq files
reseq = reseq_files[['full_path']]
reseq.columns = ['path']
all_files = all_files.append(reseq, ignore_index=True)
all_files.loc[all_files['subset'].isna(), 'subset'] = 'reseq'
all_files.loc[all_files['source'].isna(), 'source'] = 'nanopore'

# Save table
all_files.to_csv(outfile, sep=';', index=False)
print('File has been saved: {}'.format(outfile))

