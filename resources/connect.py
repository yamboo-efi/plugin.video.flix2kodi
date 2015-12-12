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
MAX_SESSIONS=5
sessions = {}
blockedSessions = []

def create_sessions():
    for i in range(0, MAX_SESSIONS-1):
        sessions[i] = create_session(i)

def create_session(idx):
    session = requests.Session()
    session.mount('https://', HTTPSAdapter())
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '

                                          'like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586'})
    session.max_redirects = 5
    session.allow_redirects = True
    if xbmcvfs.exists(utility.session_file(idx)):
        file_handler = xbmcvfs.File(utility.session_file(idx), 'rb')
        content = file_handler.read()
        file_handler.close()
        session = pickle.loads(content)
    return session

def sync_sessions():
    for i in range(1, MAX_SESSIONS-1):
        session = sessions[i]
        session.cookies = sessions[0].cookies
        save_session(session, i)

    save_session(sessions[0], 0)


def save_session(session, idx):
    temp_file = utility.session_file(idx) + '.tmp'
    if xbmcvfs.exists(temp_file):
        xbmcvfs.delete(temp_file)
    session_backup = pickle.dumps(session)
    file_handler = xbmcvfs.File(temp_file, 'wb')
    file_handler.write(session_backup)
    file_handler.close()
    if xbmcvfs.exists(utility.session_file(idx)):
        xbmcvfs.delete(utility.session_file(idx))
    xbmcvfs.rename(temp_file, utility.session_file(idx))

def synchronized(func):

    func.__lock__ = threading.Lock()

    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func

@synchronized
def get_session(first = False):
    sessionIdx = -1
    if first == True:
        tmpsession = sessions[0];
        if tmpsession not in blockedSessions:
            sessionIdx = 0
    else:
        for i in range(0, MAX_SESSIONS-1):
            tmpsession = sessions[i]
            if tmpsession not in blockedSessions:
                sessionIdx = i
                break

    session = None
    if(sessionIdx != -1 ):
        session = sessions[sessionIdx]
        blockedSessions.append(session)
    return session

def load_site_login(url, post=None, clearCookies=False):
    return load_site(url, post=post, useFirstSession = True, clearCookies=clearCookies)

def load_site(url, headers=None, post=None, options=False, cookies=None, useFirstSession = False, clearCookies=False):
    utility.log('Loading url: ' + url)

    session = None
    while (session == None):
        time.sleep(0.1)
        session = get_session(useFirstSession)
    if clearCookies == True:
        session.cookies.clear()

    if post:
        response = session.post(url, headers=headers, cookies=cookies, data=post, verify=certifi.where())
    elif options:
        response = session.options(url, headers=headers, cookies=cookies, verify=certifi.where())
    else:
        response = session.get(url, headers=headers, cookies=cookies, verify=certifi.where())

    content = response.content
    blockedSessions.remove(session)
    return content
