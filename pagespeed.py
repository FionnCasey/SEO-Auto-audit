import pandas as pd
import os
import asyncio
import aiohttp
from urllib.parse import urlencode
from ratelimiter import RateLimiter
import json

BASE_URL = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?'

def generate_url(url, strategy, key):
	params = {
		'key': key,
		'url': url,
		'strategy': strategy
	}
	return f'{BASE_URL}{urlencode(params)}'

async def fetch_one(client, url, results):
	async with await client.get(url) as resp:
		resp = await resp.json()
		try:
			page = resp['id']
			print(f'\rNow analysing: {page}', flush=True, end='				')
			data = {
				'landing_page': resp['id'],
				'overall_speed': resp['loadingExperience']['overall_category'],
				'first_contentful_paint': resp['lighthouseResult']['audits']['metrics']['details']['items'][0]['firstContentfulPaint'],
				'first_meaningful_paint': resp['lighthouseResult']['audits']['metrics']['details']['items'][0]['firstMeaningfulPaint'],
				'input_latency': resp['lighthouseResult']['audits']['metrics']['details']['items'][0]['estimatedInputLatency'],
				'time_to_interactive': resp['lighthouseResult']['audits']['metrics']['details']['items'][0]['interactive'],
				'speed_index': resp['lighthouseResult']['audits']['metrics']['details']['items'][0]['speedIndex']
			}
			results.append(data)
		except KeyError:
			try:
				error = resp['error']['message']
				print(f'Error: {error}', end='\r', flush=True)
			except KeyError:
				pass


async def fetch_all(urls, results):
	async with aiohttp.ClientSession() as client:
		client = RateLimiter(client)
		tasks = [asyncio.ensure_future(fetch_one(client, url, results)) for url in urls]
		await asyncio.gather(*tasks)

async def create_pagespeed_report():
	directory_root = os.getcwd()
	results = []
	df = pd.read_csv(directory_root + '\\output\\audit_results.csv')
	values = df.query('status_code == 200 & sessions > 0')['landing_page'].values
	urls = []

	with open('credentials/api_keys.json') as key_file:
		keys = json.load(key_file)
		api_key = keys['PAGE_SPEED']	
		urls = [generate_url(url, 'desktop', api_key) for url in values]

	print('Starting page speed analysis -- this can take a very long time!')
	print('Number of valid URLs: %s' % str(len(urls)))

	await fetch_all(urls, results)
	df = pd.DataFrame(results)
	df.to_csv('output/pagespeed_data.csv', index=False)
	print('\nCSV created successfully')


if __name__ == '__main__':
	create_pagespeed_report()