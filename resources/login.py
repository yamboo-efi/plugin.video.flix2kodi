from __future__ import unicode_literals

import json
import re
import xbmc
import xbmcgui

import connect
import profiles
import utility


def login():
    login_progress = xbmcgui.DialogProgress()
    login_progress.create('Netflix', utility.get_string(30200) + '...')
    utility.progress_window(login_progress, 25, utility.get_string(30201))
    response = connect.load_netflix_site(utility.main_url + 'Login', new_session=True)
    content = utility.decode(response)
    if not 'Sorry, Netflix ' in content:
        match = re.compile('name="authURL" value="(.+?)"', re.DOTALL).findall(content)
        utility.log('Setting authorization url: ' + match[0])
        utility.set_setting('authorization_url', match[0])
        match = re.compile('locale: "(.+?)"', re.DOTALL).findall(content)
        utility.set_setting('language', match[0])
        post_data = {'authURL': utility.get_setting('authorization_url'), 'email': utility.get_setting('username'),
                     'password': utility.get_setting('password'), 'RememberMe': 'on'}
        utility.progress_window(login_progress, 50, utility.get_string(30202))
        response = connect.load_netflix_site(utility.main_url + 'Login?locale=' + utility.get_setting('language'),
                                         post=post_data)
        content = utility.decode(response)
        xbmc.log(response)

        if 'id="page-LOGIN"' in content:
            utility.notification(utility.get_string(30303))
            return False
        match = re.compile('"apiUrl":"(.+?)",').findall(content)
        utility.set_setting('api_url', match[0])
        connect.set_chrome_netflix_cookies()
#        post_data = utility.my_list % utility.get_setting('authorization_url')
#        content = utility.decode(connect.load_netflix_site(utility.evaluator(), post=post_data))
#        matches = json.loads(content)['value']
#        match = matches['lolomos'].keys()
#        utility.set_setting('root_list', match[0])
#        match = matches['lists'].keys()
#        utility.set_setting('my_list', match[1])
#        match = matches['lists'][utility.get_setting('my_list')]['trackIds']['trackId']
#        utility.set_setting('track_id', unicode(match))
        utility.progress_window(login_progress, 75, utility.get_string(30203))
        if not (utility.get_setting('selected_profile') or (utility.get_setting('single_profile') == 'true')):
            profiles.choose()
        elif not (utility.get_setting('single_profile') == 'true') and (utility.get_setting('show_profiles') == 'true'):
            profiles.choose()
        elif not ((utility.get_setting('single_profile') and utility.get_setting('show_profiles')) == 'true'):
            profiles.load()

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
