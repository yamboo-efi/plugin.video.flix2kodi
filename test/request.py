# from __future__ import unicode_literals

import re
import json
import pprint

import sys
from requests.packages import urllib3

from resources import connect, utility

urllib3.disable_warnings()

authorization_url = None
language = None
api_url = None
main_url = 'https://www.netflix.com/'

email = sys.argv[1]
password=sys.argv[2]



def dump_login_content(content):
    file_handler = open('login_content', 'wb')
    file_handler.write(content.encode('utf-8'))
    file_handler.close()

def read_login_content():
    file_handler = open('login_content', 'rb')
    content = file_handler.read().decode('utf-8')
    file_handler.close()
    return content

def login():
    global authorization_url, language, api_url
    content = connect.load_netflix_site(main_url + 'Login', new_session=True)
    if not 'Sorry, Netflix ' in content:
        set_auth_url(content)
        match = re.compile('locale: "(.+?)"', re.DOTALL).findall(content)
        language = match[0]
        post_data = {'authURL': authorization_url, 'email': email,
                     'password': password, 'RememberMe': 'on'}
        content = connect.load_netflix_site(main_url + 'Login?locale=' + language,
                                            post=post_data)
        if 'id="page-LOGIN"' in content:
            return False
        set_api_url(content)
        dump_login_content(content)
        return True
    else:
        return False

def extract_mylist_id(jsondata):
    mylist_id = None
    try:
        assert 'lolomos' in jsondata
        lolomos = jsondata['lolomos']
        filter_size(lolomos)
        assert len(lolomos)==1
        root_list_id = lolomos.keys()[0]
        lists = filter_size(lolomos[root_list_id])
        assert 'mylist' in lists
        mylist_ref = lists['mylist']
        assert len(mylist_ref) == 3
        mylist_idx = mylist_ref[2]
        assert mylist_idx in lists
        mylist = lists[mylist_idx]
        assert len(mylist) == 2
        mylist_id = mylist[1]
    except Exception as ex:
        print('cannot find mylist_id')
        print repr(ex)
    return mylist_id

def filter_size(lolomos):
    for key in lolomos.keys():
        if key in ('$size', 'size'):
            del lolomos[key]
    return lolomos

def set_auth_url(content):
    global authorization_url
    match = re.compile('name="authURL" value="(.+?)"', re.DOTALL).findall(content)
    authorization_url = match[0]


def set_api_url(content):
    global api_url
    match = re.compile('"apiUrl":"(.+?)",').findall(content)
    api_url = match[0]

def pprint_json(str):
    jsonstr = json.loads(str)
    pprint.pprint(jsonstr)

do_login = True
real_login = False

if do_login:
    if real_login:
        if login()==True:
            print 'login successfull'
        else:
            print 'login failed!'
            exit()
    else:
        print 'loading data from disk'
        content = read_login_content()
        set_api_url(content)
        authorization_url = '1451670084901.8mhaxKFm4s75bFyJ/Ajk66cEfUV8='




############################################################################
############################################################################

content = connect.load_netflix_site("https://www.netflix.com/", new_session=False)
#pprint.pprint(content)
falkor_cache = utility.parse_falkorcache(content)
pprint.pprint(falkor_cache)

pprint.pprint(extract_mylist_id(falkor_cache))

#if logged_in(content) == True:
#    print 'logged in'
#else:
#    print 'not logged in'

#response = connect.load_netflix_site('http://www.netflix.com/')

#print response
#jsondata = utility.parse_falkorcache(content)
#print jsondata
#mylist_id = extract_mylist_id(jsondata)

#url = api_url+'/pathEvaluator?materialize=true&model=harris'
#pprint_json('')

post = '{"paths":['
list = '1'
post += '["lists","'+list+'",{"from":0,"to":19},["summary", "title"]]'

content = connect.load_netflix_site('https://www.netflix.com/api/shakti/7ffaa7f72/pathEvaluator?materialize=true&model=harris', post)
#pprint.pprint(json.loads(content))
print content
