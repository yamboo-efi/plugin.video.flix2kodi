from __future__ import unicode_literals

import pickle
import re
import requests

from resources.utility import generic_utility

from resources import login
from resources.login import CannotRefreshDataException

from resources.utility import file_utility

if not generic_utility.android():
    from resources import chrome_cookie


requests.packages.urllib3.disable_warnings()

test = False

def set_test():
    global test
    test = True


# thx to https://lukasa.co.uk/2013/01/Choosing_SSL_Version_In_Requests/
if not test:
    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.poolmanager import PoolManager
    import ssl

    class MyAdapter(HTTPAdapter):
        def init_poolmanager(self, connections, maxsize, block=False):
            self.poolmanager = PoolManager(num_pools=connections,
                                           maxsize=maxsize,
                                           block=block,
                                           ssl_version=ssl.PROTOCOL_TLSv1)
def create_session(netflix=False):

    session = requests.Session()
    if not test:
        session.mount('https://', MyAdapter())
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '

                                          'like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586'})
    session.max_redirects = 5
    session.allow_redirects = True

    if netflix == True:
        session.cookies.set('profilesNewUser', '0')
        session.cookies.set('profilesNewSession', '0')
    return session

def save_cookies(session):
    cookies =  pickle.dumps(session.cookies)

    if test == False:
        file_name = generic_utility.cookies_file()
    else:
        file_name = 'cookies'

    file_utility.write(file_name, cookies)


def read_cookies():
    if not test:
        file_name = generic_utility.cookies_file()
    else:
        file_name = 'cookies'
    content = file_utility.read(file_name)
    if len(content) > 0:
        loaded = pickle.loads(content)
        if type(loaded) == requests.cookies.RequestsCookieJar:
            return loaded
        else:
            return None
    else:
        generic_utility.log('warning, read empty cookies-file')
        return None

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
    if len(content) > 0:
        return pickle.loads(content)
    else:
        generic_utility.log('warning, read empty headers-file')
        return None


def should_retry(url, status_code):
    should = False
    if 'redirected' == status_code or (status_code in(401, 404) and '/shakti/' in url):
        should = True

    return should


def load_netflix_site(url, post=None, new_session=False, lock = None, login_process = False, options = False):

    generic_utility.debug('Loading netflix: ' + url + ' Post: ' + str(post))
    if lock != None:
        lock.acquire()

    session = get_netflix_session(new_session)

    try:
        ret, status_code = load_site_internal(url, session, post, netflix=True, options=False)
        ret = ret.decode('utf-8')
        not_logged_in = '"template":"torii/nonmemberHome.jsx"' in ret
    except requests.exceptions.TooManyRedirects:
        status_code = 'redirected'

    if status_code != requests.codes.ok or (not_logged_in and not login_process):
        if not test and not login_process and (should_retry(url, status_code) or not_logged_in):
            if lock:
                lock.release()

            try:
                refresh_data()
            except CannotRefreshDataException:
                if not do_login():
                    raise ValueError('re-login failed')

            session = get_netflix_session(new_session)
            ret, status_code = load_site_internal(url, session, post, netflix=True, options=False)
            ret = ret.decode('utf-8')
            if status_code != requests.codes.ok:
                    raise ValueError('!HTTP-ERROR1!: '+str(status_code)+' loading: "'+url+'", post: "'+ str(post)+'"')

        else:
            raise ValueError('!HTTP-ERROR2!: '+str(status_code)+' loading: "'+url+'", post: "'+ str(post)+'"')

    save_cookies(session)
    save_headers(session)

    if lock:
        lock.release()

    try_to_read_auth_url(ret)

#    generic_utility.debug('Returning : '+ret)
    return ret


def try_to_read_auth_url(ret):
    match = re.compile('"authURL":"(.+?)"', re.DOTALL | re.UNICODE).findall(ret)
    if len(match) > 0:
        authurl = generic_utility.replace_netfix_secret_code(match[0])
        generic_utility.debug('Setting authorization url: ' + authurl)
        if not test:
            generic_utility.set_setting('authorization_url', authurl)
        else:
            return authurl
    else:
        match = re.compile('name="authURL" value="(.+?)"', re.DOTALL | re.UNICODE).findall(ret)
        if len(match) > 0:
            authurl = generic_utility.replace_netfix_secret_code(match[0])

            generic_utility.debug('Setting authorization url: ' + authurl)
            if not test:
                generic_utility.set_setting('authorization_url', authurl)
            else:
                    return authurl


def get_netflix_session(new_session):
    if new_session == True:
        session = create_session(netflix=True)
    else:
        session = requests.Session()
        cached_headers = read_headers()
        if cached_headers:
            session.headers = cached_headers

        cached_cookies = read_cookies()
        if cached_cookies:
            session.cookies = cached_cookies
            session.cookies.clear_expired_cookies()
    return session


def load_other_site(url):
    generic_utility.debug('loading-other: ' + url)
    session = create_session()
    content = load_site_internal(url, session)[0]
    return content

def load_site_internal(url, session, post=None, options=False, headers=None, cookies=None, netflix=False):
    session.max_redirects = 10

    if options:
        response = session.options(url, headers=headers, cookies=cookies, verify=False)
        if response.status_code != 200:
            generic_utility.error('error options! url: '+url)
            response.raise_for_status()
    if post:
        response = session.post(url, headers=headers, cookies=cookies, data=post, verify=False)
    else:
        response = session.get(url, headers=headers, cookies=cookies, verify=False)

    content = response.content
    status = response.status_code
    return content, status


def set_chrome_netflix_cookies():
    if not generic_utility.android():
        if test == False:
            chrome_cookie.set_netflix_cookies(read_cookies())


def logged_in(content):
    return 'netflix.falkorCache' in content


def choose_profile():
    login.choose_profile()


def do_login():
    return login.login()


def refresh_data():
    login.refresh_data()
