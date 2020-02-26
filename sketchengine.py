import requests

USERNAME = 'Fionn'
API_KEY = ''
BASE_URL = 'https://api.sketchengine.eu/bonito/run.cgi'

def get_sketch():
	data = {
		'format': 'json',
		'lemma': 'book',
		'lpos': '-v'
	}
	res = requests.get(BASE_URL + '/wsketch?corpname=preloaded/bnc2', params=data, auth=(USERNAME, API_KEY)).json()
	print(res)
	print('There are %d grammar relations for %s%s (lemma + POS) in corpus %s.' %
		(len(res['Gramrels']), data['lemma'], data['lpos'], data['corpname']))

if __name__ == '__main__':
	get_sketch()