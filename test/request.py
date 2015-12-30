from __future__ import unicode_literals

import re

import sys
from requests.packages import urllib3

from resources import connect

urllib3.disable_warnings()

authorization_url = None
language = None
api_url = None
main_url = 'https://www.netflix.com/'

email = sys.argv[1]
password=sys.argv[2]

def login():
    global authorization_url, language, api_url
    content = connect.load_netflix_site(main_url + 'Login', new_session=True)
    if not 'Sorry, Netflix ' in content:
        match = re.compile('name="authURL" value="(.+?)"', re.DOTALL).findall(content)
        authorization_url = match[0]
        match = re.compile('locale: "(.+?)"', re.DOTALL).findall(content)
        language = match[0]
        post_data = {'authURL': authorization_url, 'email': email,
                     'password': password, 'RememberMe': 'on'}
        content = connect.load_netflix_site(main_url + 'Login?locale=' + language,
                                            post=post_data)
        if 'id="page-LOGIN"' in content:
            return False
        match = re.compile('"apiUrl":"(.+?)",').findall(content)
        api_url = match[0]

        return True
    else:
        return False


if login()==True:
    print 'login successfull'
else:
    print 'login failed!'
    exit()

############################################################################
############################################################################



url = api_url+'/pathEvaluator?materialize=true&model=harris'
#post = '{"paths":[["videos",60032563,["availability","bookmarkPosition","details","episodeCount","maturity","queue","releaseYear","requestId","runtime","seasonCount","summary","title","userRating","watched"]],["videos",60032563,"current",["summary","runtime","bookmarkPosition","creditsOffset","title"]],["videos",60032563,"seasonList","current",["showMemberType","summary"]],["videos",60032563,"boxarts",["_342x192","_665x375"],"jpg"]],"authURL":"1451406845694.A/NkMzIpaw/Hmf+ZlF41GuuVE9o="}'
#post = '{"paths":[["videos",60032563,["userRating"]]],"authURL":"'+authorization_url+'"}'
post = '{"paths":[["videos",60032563,"boxarts",["_342x192","_665x375"],"jpg"]],"authURL":"'+authorization_url+'"}'

content = connect.load_netflix_site(url, post)

# logi85
# Loading: https://www.netflix.com/api/shakti/XXXX/pathEvaluator?materialize=true&model=harris Post: {"paths":[["videos",60032563,["userRating"]]],"authURL":"XXXXXXXXXXXXXXXX"}
# Returning: {"value":{"videos":{"60032563":{"userRating":{"average":3.8649237,"predicted":3.9,"userRating":null,"type":"star","$type":"leaf"}}}},"paths":[["videos","60032563",["userRating"]]]}
