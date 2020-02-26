import argparse
from apiclient.discovery import build
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools
import numpy as np
import pandas as pd
import re
import os

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, parents=[tools.argparser])
flags = parser.parse_args([])

def initialise_analytics(ga_account):
    directory_root = os.getcwd()
    key_file_location = directory_root + '\\credentials\\credentials.json'
    flow = client.flow_from_clientsecrets(key_file_location, scope=SCOPES, message=tools.message_if_missing(key_file_location))
    storage = file.Storage(directory_root + '\\credentials\\' + ga_account + '.dat')
    credentials = storage.get()
    
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage, flags)

    http = credentials.authorize(http=httplib2.Http())
    analytics = build('analyticsreporting', 'v4', http=http)
    return analytics
    
def make_request(analytics, body):
    return analytics.reports().batchGet(body=body).execute()

def print_response(response):
    for report in response.get('reports', []):
        column_headers = report.get('columnHeader', {})
        dimension_headers = column_headers.get('dimensions', [])
        metric_headers = column_headers.get('metricHeader', {}).get('metricHeaderEntries', [])
        
        for row in report.get('data', {}).get('rows', []):
            dimensions = row.get('dimensions', [])
            metrics = row.get('metrics', [])
            
            for header, dimension in zip(dimension_headers, dimensions):
                print('%s: %s' % (header, dimension))
            
            for i, values in enumerate(metrics):
                print('Date Range: %s' % str(i))
                for metric_header, value in zip(metric_headers, values.get('values')):
                    print('%s: %s' % (metric_header.get('name'), value))
                    
def create_data_frame(response):
    reports = response.get('reports', [])
    
    if len(reports) > 0:
        column_headers = reports[0].get('columnHeader', [])
        dimension_headers = [dimension.replace('ga:', '') for dimension in column_headers.get('dimensions', [])]
        metric_headers = column_headers.get('metricHeader', {}).get('metricHeaderEntries', [])
        csv_headers = [header.get('name').replace('ga:', '') for header in metric_headers]
        headers = np.concatenate((dimension_headers, csv_headers), axis=None).tolist()
        data = []
                             
        for row in reports[0].get('data', {}).get('rows', []):
            dimensions = row.get('dimensions', [])
            metrics = np.array([metric.get('values') for metric in row.get('metrics', [])]).flatten().tolist()
            data.append(np.concatenate((dimensions, metrics), axis=None).tolist())
        
        df = pd.DataFrame(data, columns=headers)
        return df
            
    else:
        print('No data found')

def format_data_frame(df, base_url):
    df.rename(columns={ 'landingPagePath': 'landing_page' }, inplace=True)
    df['landing_page'] = df['landing_page'].apply(lambda x: base_url + re.sub(r'\?.+$', '', x))
    return df

def create_ga_report(analytics, base_url, view, start, end):
    body = {
        'reportRequests': [{
            'viewId': view,
            'dateRanges': [{ 'startDate': start, 'endDate': end }],
            'metrics': [
                { 'expression': 'ga:users' },
                { 'expression': 'ga:newUsers', 'alias': 'new_users' },
                { 'expression': 'ga:sessions' },
                { 'expression': 'ga:bounceRate', 'alias': 'bounce_rate' },
                { 'expression': 'ga:pageViewsPerSession', 'alias': 'pages_per_session' },
                { 'expression': 'ga:avgSessionDuration', 'alias': 'session_duration' },
                { 'expression': 'ga:transactionsPerSession', 'alias': 'conversion_rate' },
                { 'expression': 'ga:transactions' },
                { 'expression': 'ga:transactionRevenue', 'alias': 'revenue' }
            ],
            'dimensions': [
                { 'name': 'ga:landingPagePath' }
            ],
            'pageSize': '50000',
            'orderBys': [
                { 'fieldName': 'ga:transactionRevenue', 'sortOrder': 'DESCENDING' },
                { 'fieldName': 'ga:sessions', 'sortOrder': 'DESCENDING' }
            ]
        }]
    }
    response = make_request(analytics, body)
    df = format_data_frame(create_data_frame(response), base_url)
    df.to_csv('output/ga_data.csv', index=False)
    print('CSV created successfully')

def get_model_data(analytics, view, start, end):
    body = {
        'reportRequests': [{
            'viewId': view,
            'dateRanges': [{ 'startDate': start, 'endDate': end }],
            'metrics': [
                { 'expression': 'ga:users' },
                { 'expression': 'ga:newUsers', 'alias': 'new_users' },
                { 'expression': 'ga:sessions' },
                { 'expression': 'ga:bounceRate', 'alias': 'bounce_rate' },
                { 'expression': 'ga:pageViewsPerSession', 'alias': 'pages_per_session' },
                { 'expression': 'ga:avgSessionDuration', 'alias': 'session_duration' },
                { 'expression': 'ga:transactionsPerSession', 'alias': 'conversion_rate' },
                { 'expression': 'ga:transactions' },
                { 'expression': 'ga:transactionRevenue', 'alias': 'revenue' }
            ],
            'dimensions': [
                { 'name': 'ga:date' }
            ],
            'pageSize': '50000'
        }]
    }
    response = make_request(analytics, body)
    df = create_data_frame(response)
    df.to_csv('output/model_data.csv', index=False)
    print('CSV created successfully')