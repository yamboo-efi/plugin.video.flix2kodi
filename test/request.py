# from __future__ import unicode_literals

import json
import os
import pickle
import pprint
import re
import sys
from requests.packages import urllib3
from time import sleep

from resources import connect
from resources.utility import generic_utility
from resources.utility import file_utility



def get_video_ids(directory):
    video_ids = []
    files= []
    for dirpath, dirnames, filenames in os.walk(directory+os.sep):
        for filename in [f for f in filenames if f.decode('utf-8').endswith("V.strm")]:
            files.append(os.path.join(dirpath, filename).decode('utf-8'))

    for curfile in files:
        video_id = re.search('\.V(.*)V\.strm', curfile).group(1)
        video_ids.append(video_id)
    return video_ids

urllib3.disable_warnings()
connect.set_test()

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


def extract_mylist_id(falkor_cache):
    mylist_id = None
    try:
        assert 'lolomos' in falkor_cache
        lolomos = falkor_cache['lolomos']
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


#profile-switcher
content = connect.load_netflix_site('https://www.netflix.com/api/shakti/c88e2062/profiles/switch?switchProfileGuid=HC2AFIZSMRHCDPZ76LZZRENGSI&authURL=%s' % authorization_url)

############################################################################
############################################################################

sleep(1)


#content = connect.load_netflix_site("http://www.netflix.com/browse", new_session=False)
#falkor_cache = generic_utility.parse_falkorcache(content)
#extract_mylist_id(falkor_cache)
#pprint.pprint(falkor_cache['lists'])

#pprint.pprint(falkor_cache['videos'])


#list = '402ccb6f-4c0f-47b5-8d6e-906f40b16b16_8101754'


#list = '19362395-0693-4501-b6c6-5af7c75aaf35_14096548'
#post = '{"paths":['
#post += '["lists","'+list+'","trackIds", {"from":0,"to":999},["summary","title"]]]'
#post += '["videos",["70122827","70122838"],["bookmarkPosition", "runtime"]]'
#post += '],"authURL":"%s"}' % authorization_url


post = '{"callPath":["lolomos","0e50e9d5-9c44-4ad8-a106-691c0742ffff_ROOT","addToList"],'+\
       '"params":["0e50e9d5-9c44-4ad8-a106-691c0742ffff_53724068",2,["videos",80042368],13630398,null,null],'+\
       '"authURL":"1452206880591.tSgtf4/ICsBChqVNTmYCBVA871E="}'

#post = '{"callPath":["lolomos","19362395-0693-4501-b6c6-5af7c75aaf35_ROOT","addToList"],'+\
#       '"params":["19362395-0693-4501-b6c6-5af7c75aaf35_14096548",2,["videos",70080038],13462260,null,null],'+\
#       '"authURL":"1452201279843.P+9yGC0A/W+XLMmWeegiACUgvdA="}'
content = connect.load_netflix_site('https://www.netflix.com/api/shakti/c88e2062/pathEvaluator?materialize=true&model=harris&method=call', post)
jsn = json.loads(content)
pprint.pprint(jsn)





#matches = json.loads(content)#['value']['videos']
#pprint.pprint(matches)
#pprint.pprint(json.loads(content))
#print content



