# from __future__ import unicode_literals

import json
import pickle
import pprint
import re
import sys
from requests.packages import urllib3

from resources import connect
from resources.utility import generic_utility
from resources.utility import file_utility

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
        authorization_url = sys.argv[3]




############################################################################
############################################################################

content = connect.load_netflix_site("https://www.netflix.com/", new_session=False)
#pprint.pprint(content)
falkor_cache = generic_utility.parse_falkorcache(content)

print 'mylist: '+extract_mylist_id(falkor_cache)


def read_lists():
    lists = falkor_cache['lists']
    lists = filter_size(lists)
    rets = []
    videos=[]
    for list_key in lists:
        list = lists[list_key]
        list = filter_size(list)
        if 'displayName' in list:
            display_name = unicode(list['displayName']['value'])
            ret = {'id': list_key, 'name': display_name}
            rets.append(ret)
    return rets

lists = read_lists()
#for list in read_lists():
#    print 'id: '+list['id']+' name: '+list['name']


list = lists[0]['id']

#post = '{"paths":['
#post += '["lists","'+list+'",{"from":0,"to":19},["summary", "title"]]'
#post += '],"authURL":"%s"}' % authorization_url


post = '{"paths":[["search","%s",{"from":0,"to":48},["summary","title"]],["search","%s",["id","length",' \
            '"name","trackIds","requestId"]]],"authURL":"%s"}' % ('Hobbit', 'Hobbit',
                                                                  authorization_url)


content = connect.load_netflix_site('https://www.netflix.com/api/shakti/7ffaa772/pathEvaluator?materialize=true&model=harris', post)

matches = json.loads(content)['value']['videos']
pprint.pprint(matches)
#pprint.pprint(json.loads(content))
#print content



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

