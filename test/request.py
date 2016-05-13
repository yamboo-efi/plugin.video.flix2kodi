# from __future__ import unicode_literals
import Cookie
import os
import pprint
import re
import sys
from requests.packages import urllib3
from time import sleep

import datetime

from resources import connect, video_parser
from resources.path_evaluator import *
from resources.path_evaluator.types import lolomos

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
    content = connect.load_netflix_site(main_url + 'Login', new_session=True, login_process=True)
    if not 'Sorry, Netflix ' in content:

        set_auth_url(connect.try_to_read_auth_url(content))
        match = re.compile('locale: "(.+?)"', re.DOTALL).findall(content)
        language = match[0]
        authorization_url = connect.try_to_read_auth_url(content)

        post_data = {'authURL': authorization_url, 'email': email,
                     'password': password, 'RememberMe': 'on'}
        content = connect.load_netflix_site(main_url + 'Login?locale=' + language,
                                            post=post_data, login_process=True)
        if 'id="page-LOGIN"' in content:
            return False
        set_api_url(content)
        authorization_url = connect.try_to_read_auth_url(content)
        dump_login_content(content)
        return True
    else:
        return False


def filter_size(lolomos):
    for key in lolomos.keys():
        if key in ('$size', 'size'):
            del lolomos[key]
    return lolomos

def set_auth_url(aurl):
    global authorization_url
    authorization_url = aurl
    generic_utility.set_setting('authorization_url', authorization_url)


def set_api_url(content):
    global api_url
    match = re.compile('"apiUrl":"(.+?)",').findall(content)
    api_url = match[0]
    generic_utility.set_setting('api_url', api_url)

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
        authorization_url = connect.try_to_read_auth_url(content)
        set_auth_url(authorization_url)


#profile-switcher
#content = connect.load_netflix_site('https://www.netflix.com/api/shakti/c88e2062/profiles/switch?switchProfileGuid=HC2AFIZSMRHCDPZ76LZZRENGSI&authURL=%s' % authorization_url)

############################################################################
############################################################################

sleep(0.5)


root_list = '' #'384181da-ca38-4e67-8411-05d15c51927c_ROOT'

#jsn = req_path(api_url, authorization_url, lolomos.my_list(''), lolomos.lists(''))


#jsn = req_path(lolomos.my_list(root_list), lolomos.lists(root_list))


root_list_id = lolomos.get_root_list()

pprint.pprint(root_list_id)
#filter_empty(jsn)
#jsn = req_path(path('"lolomos"', '"-1"', from_to(0, 10), '"displayName"'))


#mylist, my_data = lolomos.get_mylist(root_list_id)

#pprint.pprint(mylist)
#70248297,70189472
search_str = 'Gretel'

off_from = 0
off_to = 100
genre_to_browse = '7442'
video_infos1 = '["requestId","availability","bookmarkPosition","details","episodeCount","maturity",' \
               '"queue","releaseYear","requestId","runtime","seasonCount","summary","title","userRating","watched"]'
video_infos2 = '"current",["summary","runtime","bookmarkPosition","creditsOffset","title"]'
video_infos3 = '"seasonList","current",["showMemberType","summary"]'
video_infos4 = '"boxarts",["_665x375","_342x192"],"jpg"'


#path1 = path('"genres"', genre_to_browse, '["length"]')
#path2 = path('"genres"', genre_to_browse, '"su"', from_to(off_from, off_to), video_infos1)
#path3 = path('"genres"', genre_to_browse, '"su"', from_to(off_from, off_to), video_infos2)
#path4 = path('"genres"', genre_to_browse, '"su"', from_to(off_from, off_to), video_infos3)
#path5 = path('"genres"', genre_to_browse, '"su"', from_to(off_from, off_to), video_infos4)

#pathvid = path('"videos"', '70306296', '["requestId"]')

pathvid = '["lolomos","-1",{"from":0,"to":1},"displayName"]'
ret = req_path(pathvid)#, path2, path3, path4, path5)
filter_empty(ret)



#connect.load_netflix_site("http://www.netflix.com/browse")
print(json.dumps(ret))



