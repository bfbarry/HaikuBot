import requests
import json

with open('../_auth/reddit.json') as f:
    config = json.load(f)
    
base_url = 'https://www.reddit.com/'
data = {'grant_type': 'password', 'username': config['username'], 'password': config['password']}
auth = requests.auth.HTTPBasicAuth(config['app_key'], config['app_secret'])
r = requests.post(base_url + 'api/v1/access_token',
                  data=data,
                  headers={'user-agent': config['user-agent']},
		  auth=auth)
d = r.json()

token = 'bearer ' + d['access_token']

base_url = 'https://oauth.reddit.com'

headers = {'Authorization': token, 'User-Agent': config['user-agent']}
response = requests.get(base_url + '/api/v1/me', headers=headers)

def access_valid():
    return response.status_code == 200

def scrape_haiku(sort='top',size=1000):
    '''Size actually shrinks when removing duplicates'''
    titles = []
    after = None
    while len(titles) < size:
        payload = {'t':'all','limit':100,'after':after}
        response = requests.get(base_url + f'/r/haiku/{sort}', headers=headers, params=payload)
        values = response.json()
        after = values['data']['after'] # to reset index
        curr_titles = [ values['data']['children'][i]['data']['title'] 
                         for i in range(len(values['data']['children'])) ]
        curr_titles = [t for t in curr_titles if '/' in t]
        titles += [*curr_titles]
    titles_clean = []
    [titles_clean.append(t.replace('//', '/')) # keep consistent '/' format
            for t in titles if t not in titles_clean] #remove duplicates
    return titles_clean