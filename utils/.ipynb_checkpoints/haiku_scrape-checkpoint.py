import requests
import json
import unicodedata as ud
import string

with open('../../_auth/reddit.json') as f:
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

def replace_all(in_str, unwanted, sub = '/'):
    """
    Removes all instances of an unwanted string inside in_str
    """
    for i in unwanted:
        in_str = in_str.replace(i, sub)
    return in_str

### From https://stackoverflow.com/questions/3094498/how-can-i-check-if-a-python-unicode-string-contains-non-western-letters ###
latin_letters= {}
def is_latin(uchr):
    try: return latin_letters[uchr]
    except KeyError:
         return latin_letters.setdefault(uchr, 'LATIN' in ud.name(uchr))

def is_roman(unistr):
    return all(is_latin(uchr)
           for uchr in unistr
           if uchr.isalpha()) 

def pref_ch(ch):
    """(Bool) checks if character ch is preferable for the data"""
    ok_char = [' ', "'",'"','“', '”', ',','.','!','?'] + ['/']
    return ch.isalpha() or ch in ok_char

def pref_form(haiku):
    """ (Bool) check if haiku is of preferred format stanza1 / stanza2 / stanza3 """
    #counting chars w/in list comp is awkward but works
    return sum([0 if is_roman(i) and pref_ch(i) and haiku.count('/') == 2 else 1 for i in haiku ]) == 0

def rm_emojis(haiku):
    for c in haiku:
        if ord(c) > 8000: # kind of arbitrary but most emojis are around here
            haiku = haiku.replace(c,'')
    return haiku
            

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
        curr_titles = [t for t in curr_titles if '/' in t] # first pass check if it is a haiku
        titles += [*curr_titles] #ie extend
    titles_clean = []
    ## CLEANING DATA ##
    # these list comps apply multiple steps of filtering/replacing
    [titles_clean.append(replace_all(t, ['//','\\','  ',' / '], '/')) # start with consistent '/' format
            for t in titles if t not in titles_clean] #remove duplicates

    titles_clean = [rm_emojis(replace_all(h, ['“', '”','"',',','.','?','!'], '')).lower() for h in titles_clean if pref_form(h)]
    titles_clean = [h.replace('/',' / ') for h in titles_clean] # want / as special char
    for ix, h in enumerate(titles_clean):
        h += " $"
        titles_clean[ix] = h
    return titles_clean

def detokenize(tokens):
    '''from https://stackoverflow.com/questions/21948019/python-untokenize-a-sentence'''
    s = "".join([" "+i if not i.startswith("'") and i not in string.punctuation else i for i in tokens]).strip()
    # special cases
#     s = s.replace('`` ','``') #sticking with weird nltk quotes for now
    s = s.replace('/',' /')
    s = s.replace('$',' $')
    return s
    