from __future__ import unicode_literals

import pickle
import requests
import ssl
import threading
import time

import xbmc
import xbmcvfs
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.exceptions import InsecurePlatformWarning
from requests.packages.urllib3.poolmanager import PoolManager

import resources.lib.certifi as certifi
import utility

requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)


class HTTPSAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)


netflix_session = None

def create_session(netflix = False, new_session = False):
    session = requests.Session()
    session.mount('https://', HTTPSAdapter())
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '

                                          'like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586'})
    session.max_redirects = 5
    session.allow_redirects = True
    if netflix == True and new_session == False and xbmcvfs.exists(utility.session_file()):
        file_handler = xbmcvfs.File(utility.session_file(), 'rb')
        content = file_handler.read()
        file_handler.close()
        session = pickle.loads(content)
    return session


def save_netflix_session():
    session_file = utility.session_file()
    temp_file = session_file + '.tmp'
    if xbmcvfs.exists(temp_file):
        xbmcvfs.delete(temp_file)
    session_backup = pickle.dumps(netflix_session)
    file_handler = xbmcvfs.File(temp_file, 'wb')
    file_handler.write(session_backup)
    file_handler.close()
    if xbmcvfs.exists(session_file):
        xbmcvfs.delete(session_file)
    xbmcvfs.rename(temp_file, session_file)

def load_netflix_site(url, post=None, new_session=False, lock = None):
    if lock != None:
        lock.acquire()

    global netflix_session
    if netflix_session == None or new_session == True:
        netflix_session = create_session(netflix=True, new_session = new_session)

    session = requests.Session()
    session.headers = netflix_session.headers.copy()
    session.cookies = netflix_session.cookies.copy()

    ret = load_site_internal(url, session, post)

    netflix_session.headers = session.headers.copy()
    netflix_session.cookies = session.cookies.copy()
    if lock != None:
        lock.release()
    return ret


def load_other_site(url):
    session = create_session()
    return load_site_internal(url, session)

def load_site_internal(url, session, post=None, options=False, headers=None, cookies=None):
    utility.log('Loading url: ' + url, xbmc.LOGDEBUG)

    if post:
        response = session.post(url, headers=headers, cookies=cookies, data=post, verify=certifi.where())
    elif options:
        response = session.options(url, headers=headers, cookies=cookies, verify=certifi.where())
    else:
        response = session.get(url, headers=headers, cookies=cookies, verify=certifi.where())

    content = response.content
    return content
