from __future__ import unicode_literals

import pickle
import requests
import ssl
import xbmc
import xbmcvfs
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.exceptions import InsecurePlatformWarning
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3.poolmanager import PoolManager

import resources.lib.certifi as certifi
import utility

requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
session = None


class HTTPSAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)


def new_session():
    global session
    session = requests.Session()
    session.mount('https://', HTTPSAdapter())
    session.headers.update({'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'})
    session.max_redirects = 5
    session.allow_redirects = True
    if xbmcvfs.exists(utility.session_file()):
        file_handler = xbmcvfs.File(utility.session_file(), 'rb')
        content = file_handler.read()
        file_handler.close()
        session = pickle.loads(content)


def save_session():
    temp_file = utility.session_file() + '.tmp'
    if xbmcvfs.exists(temp_file):
        xbmcvfs.delete(temp_file)
    session_backup = pickle.dumps(session)
    file_handler = xbmcvfs.File(temp_file, 'wb')
    file_handler.write(session_backup)
    file_handler.close()
    if xbmcvfs.exists(utility.session_file()):
        xbmcvfs.delete(utility.session_file())
    xbmcvfs.rename(temp_file, utility.session_file())


def load_site(url, post=None):
    utility.log('Loading url: ' + url)
    try:
        if post:
            response = session.post(url, data=post, verify=certifi.where())
        else:
            response = session.get(url, verify=certifi.where())
    except AttributeError:
        utility.log('Session is missing', loglevel=xbmc.LOGERROR)
        utility.notification(utility.get_string(30301))
        new_session()
        save_session()
        if post:
            response = session.post(url, data=post, verify=certifi.where())
        else:
            response = session.get(url, verify=certifi.where())
    return response.content
