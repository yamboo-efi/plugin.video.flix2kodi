from __future__ import unicode_literals

import pickle
import requests
import ssl

test = False
try:
    from resources import chrome_cookie
except Exception:
    test = True

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.exceptions import InsecurePlatformWarning
from requests.packages.urllib3.poolmanager import PoolManager

import resources.lib.certifi as certifi
from resources.utility import generic_utility
from resources.utility import file_utility

requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)


class HTTPSAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)


def create_session(netflix = False):
    session = requests.Session()
    session.mount('https://', HTTPSAdapter())
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '

                                          'like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586'})
    session.max_redirects = 5
    session.allow_redirects = True

    if netflix == True:
        session.cookies.set('profilesNewUser', '0')
        session.cookies.set('profilesNewSession', '0')
    return session

def save_cookies(session):
    cookies =  pickle.dumps(requests.utils.dict_from_cookiejar(session.cookies))

    if test == False:
        file_name = generic_utility.cookies_file()
    else:
        file_name = 'cookies'

    file_utility.write(file_name, cookies)

def read_cookies():
    if test == False:
        file_name = generic_utility.cookies_file()
    else:
        file_name = 'cookies'
    content = file_utility.read(file_name)
    return requests.utils.cookiejar_from_dict(pickle.loads(content))

def save_headers(session):
    headers =  pickle.dumps(session.headers)

    if test == False:
        headers_file = generic_utility.headers_file()
    else:
        headers_file = 'headers'

    file_utility.write(headers_file, headers)

def read_headers():
    if test == False:
        headers_file = generic_utility.headers_file()
    else:
        headers_file = 'headers'
    content = file_utility.read(headers_file)
    return pickle.loads(content)

def load_netflix_site(url, post=None, new_session=False, lock = None):
    generic_utility.debug('Loading netflix: ' + url + ' Post: ' + str(post))
    if lock != None:
        lock.acquire()

    if new_session == True:
        session = create_session(netflix=True)
    else:
        session = requests.Session()
        session.headers = read_headers()
        session.cookies = read_cookies()
    ret = load_site_internal(url, session, post)
    ret = ret.decode('utf-8')
    save_cookies(session)
    save_headers(session)

    if lock != None:
        lock.release()

#    utility.debug('Returning : '+ret)
    return ret


def load_other_site(url):
    generic_utility.log('loading-other: ' + url)
    session = create_session()
    content = load_site_internal(url, session)
    return content

def load_site_internal(url, session, post=None, options=False, headers=None, cookies=None):

    if post:
        response = session.post(url, headers=headers, cookies=cookies, data=post, verify=certifi.where())
    elif options:
        response = session.options(url, headers=headers, cookies=cookies, verify=certifi.where())
    else:
        response = session.get(url, headers=headers, cookies=cookies, verify=certifi.where())

    content = response.content
    return content

def set_chrome_netflix_cookies():
    if test == False:
        chrome_cookie.set_netflix_cookies(read_cookies())

def logged_in(content):
    return 'netflix.falkorCache' in content
