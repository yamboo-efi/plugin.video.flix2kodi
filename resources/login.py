from __future__ import unicode_literals

import json
import re

import xbmc
import xbmcgui

import connect
import profiles
import utility


def read_mylists():
    content = connect.load_netflix_site("https://www.netflix.com/")
    falkor_cache = utility.parse_falkorcache(content)
    utility.set_setting('mylist_id', extract_mylist_id(falkor_cache))



def login():
    login_progress = xbmcgui.DialogProgress()
    login_progress.create('Netflix', utility.get_string(30200) + '...')
    utility.progress_window(login_progress, 25, utility.get_string(30201))
    content = connect.load_netflix_site(utility.main_url + 'Login', new_session=True)
    if not 'Sorry, Netflix ' in content:
        match = re.compile('name="authURL" value="(.+?)"', re.DOTALL| re.UNICODE).findall(content)
#        utility.log('Setting authorization url: ' + match[0])
        utility.set_setting('authorization_url', match[0])
        match = re.compile('locale: "(.+?)"', re.DOTALL|re.UNICODE).findall(content)
        utility.set_setting('language', match[0])
        post_data = {'authURL': utility.get_setting('authorization_url'), 'email': utility.get_setting('username'),
                     'password': utility.get_setting('password'), 'RememberMe': 'on'}
        utility.progress_window(login_progress, 50, utility.get_string(30202))
        content = connect.load_netflix_site(utility.main_url + 'Login?locale=' + utility.get_setting('language'),
                                         post=post_data)
#        utility.log(content)

        if 'id="page-LOGIN"' in content:
            utility.notification(utility.get_string(30303))
            return False
        match = re.compile('"apiUrl":"(.+?)",', re.UNICODE).findall(content)
        utility.set_setting('api_url', match[0])

        connect.set_chrome_netflix_cookies()

        utility.progress_window(login_progress, 75, utility.get_string(30203))

        profile_selection()

        read_mylists()        

        if login_progress:
            if not utility.progress_window(login_progress, 100, utility.get_string(30204)):
                return False
            xbmc.sleep(500)
            login_progress.close()
        return True
    else:
        utility.notification(utility.get_string(30300))
        if login_progress:
            login_progress.close()
        return False


def profile_selection():
    if not (utility.get_setting('selected_profile') or (utility.get_setting('single_profile') == 'true')):
        profiles.choose()
    elif not (utility.get_setting('single_profile') == 'true') and (utility.get_setting('show_profiles') == 'true'):
        profiles.choose()
    elif not ((utility.get_setting('single_profile') and utility.get_setting('show_profiles')) == 'true'):
        profiles.load()


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
