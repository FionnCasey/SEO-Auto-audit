import pandas as pd
import os

AGGREGATE = {
    'users': 'sum',
    'new_users': 'sum',
    'sessions': 'sum',
    'bounce_rate': 'mean',
    'pages_per_session': 'mean',
    'session_duration': 'mean',
    'conversion_rate': 'mean',
    'transactions': 'sum',
    'revenue': 'sum'
}

def lookup(df, key, search, index, na=0):
    try:
        return df.loc[df[key] == search].values[0][index]
    except IndexError:
        return 0

def merge_ga_sf_data():
    directory_root = os.getcwd()
    ga_df = pd.read_csv(directory_root + '\\output\\ga_data.csv')
    inlinks_df = pd.read_csv(directory_root + '\\output\\all_inlinks.csv')
    df = ga_df.groupby(ga_df['landing_page']).aggregate(AGGREGATE).reset_index()
    df['internal_links'] = df['landing_page'].apply(lambda x: (inlinks_df['Source'] == x).sum())
    df['status_code'] = df['landing_page'].apply(lambda x: lookup(inlinks_df, 'Source', x, -4))
    df.to_csv('output/audit_results.csv', index=False)
    print('CSV created successfully')
    return df

def merge_pagespeed_data():
    directory_root = os.getcwd()
    pagespeed_df = pd.read_csv(directory_root + '\\output\\pagespeed_data.csv')
    audit_df = pd.read_csv(directory_root + '\\output\\audit_results.csv')
    df = pd.merge(audit_df, pagespeed_df, on='landing_page')
    df.to_csv('output/all_results.csv', index=False)
    print('CSV created successfully')
    return df