from __future__ import unicode_literals

import os
import pickle
import requests
import ssl

from resources import chrome_cookie
from resources import login

from requests.packages.urllib3.exceptions import InsecurePlatformWarning

import resources.lib.certifi as certifi
from resources.utility import generic_utility
from resources.utility import file_utility

requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)


test = False


def set_test():
    global test
    test = True


def create_session(netflix = False):
    session = requests.Session()
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
    if len(content) > 0:
        return requests.utils.cookiejar_from_dict(pickle.loads(content))
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
    if 'redirected' == status_code or (status_code == 404 and 'pathEvaluator' in url):
        should = True

    return should


def load_netflix_site(url, post=None, new_session=False, lock = None, login_process = False):

    generic_utility.debug('Loading netflix: ' + url + ' Post: ' + str(post))
    if lock != None:
        lock.acquire()

    session = get_netflix_session(new_session)

    try:
        ret, status_code = load_site_internal(url, session, post, netflix=True)
        ret = ret.decode('utf-8')
        not_logged_in = '"template":"torii/nonmemberHome.jsx"' in ret
    except requests.exceptions.TooManyRedirects:
        status_code = 'redirected'

    if status_code != requests.codes.ok or not_logged_in:
        if not login_process and (should_retry(url, status_code) or not_logged_in):
            if lock:
                lock.release()
            if do_login():
                session = get_netflix_session(new_session)
                ret, status_code = load_site_internal(url, session, post, netflix=True)
                ret = ret.decode('utf-8')
                if status_code != requests.codes.ok:
                        raise ValueError('!HTTP-ERROR!: '+str(status_code)+' loading: "'+url+'", post: "'+ str(post)+'"')
            else:
                raise ValueError('re-login failed')

        else:
            raise ValueError('!HTTP-ERROR!: '+str(status_code)+' loading: "'+url+'", post: "'+ str(post)+'"')

    save_cookies(session)
    save_headers(session)

    if lock:
        lock.release()

#    generic_utility.debug('Returning : '+ret)
    return ret


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
    return session


def load_other_site(url):
    generic_utility.log('loading-other: ' + url)
    session = create_session()
    content = load_site_internal(url, session)[0]
    return content

def load_site_internal(url, session, post=None, options=False, headers=None, cookies=None, netflix=False):
#    generic_utility.log(str(cookies))
    session.max_redirects = 10
    if post:
        response = session.post(url, headers=headers, cookies=cookies, data=post, verify=False)
    elif options:
        response = session.options(url, headers=headers, cookies=cookies, verify=False)
    else:
        response = session.get(url, headers=headers, cookies=cookies, verify=False)

    content = response.content
    status = response.status_code
    return content, status

def set_chrome_netflix_cookies():
    if test == False:
        chrome_cookie.set_netflix_cookies(read_cookies())

def logged_in(content):
    return 'netflix.falkorCache' in content

def choose_profile():
    login.choose_profile()

def do_login():
    return login.login()
