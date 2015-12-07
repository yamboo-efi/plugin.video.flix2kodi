from __future__ import unicode_literals

import re
import xbmc
import xbmcgui

import connect
import profiles
import utility


def login():
    login_progress = xbmcgui.DialogProgress()
    login_progress.create('Netflix', utility.get_string(30200) + '...')
    connect.session.cookies.clear()
    utility.progress_window(login_progress, 25, utility.get_string(30201))
    content = utility.decode(connect.load_site(utility.main_url + '/Login'))
    match = re.compile('"locale":"(.+?)"', re.DOTALL | re.IGNORECASE).findall(content)
    if match and not utility.get_setting('language'):
        utility.log('Setting language: ' + match[0])
        utility.set_setting('language', match[0])
    if not 'Sorry, Netflix ' in content:
        match = re.compile('id="signout".+?authURL=(.+?)"', re.DOTALL).findall(content)
        if match:
            utility.log('Setting authorization url: ' + match[0])
            utility.set_setting('authorization_url', match[0])
        if 'id="page-LOGIN"' in content:
            match = re.compile('name="authURL" value="(.+?)"', re.DOTALL).findall(content)
            utility.log('Setting authorization url: ' + match[0])
            utility.set_setting('authorization_url', match[0])
            post_data = {'authURL': match[0], 'email': utility.get_setting('username'),
                         'password': utility.get_setting('password'), 'RememberMe': 'on'}
            utility.progress_window(login_progress, 50, utility.get_string(30202))
            content = utility.decode(connect.load_site(utility.main_url + '/Login?locale=' +
                                                       utility.get_setting('language'), post=post_data))
            print utility.encode(content)
            if 'id="page-LOGIN"' in content:
                utility.notification(utility.get_string(30303))
                return False
            match = re.compile('"locale":"(.+?)"', re.DOTALL | re.IGNORECASE).findall(content)
            if match and not utility.get_setting('language'):
                utility.log('Setting language: ' + match[0])
                utility.set_setting('language', match[0])
            match = re.compile('"country":"(.+?)"', re.DOTALL | re.IGNORECASE).findall(content)
            if match:
                utility.log('Setting country code: ' + match[0])
                utility.set_setting('country_code', match[0])
            match = re.compile('"apiUrl":"(.+?)",').findall(content)
            if match:
                utility.set_setting('api_url', match[0])
            connect.save_session()
            utility.progress_window(login_progress, 75, utility.get_string(30203))
        if not (utility.get_setting('selected_profile') or (utility.get_setting('single_profile') == 'true')):
            profiles.choose()
        elif not (utility.get_setting('single_profile') == 'true') and (utility.get_setting('show_profiles') == 'true'):
            profiles.choose()
        elif not ((utility.get_setting('single_profile') and utility.get_setting('show_profiles')) == 'true'):
            profiles.load()
        #if not utility.get_setting('is_kid') == 'true':
            #match = re.compile('"version":{"app":"(.+?)"').findall(content)
            #utility.set_setting('lolomos', match[0])
            #3a5922fa-a4a9-41d8-a08c-9e84c2d32be4_ROOT
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
