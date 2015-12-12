from __future__ import unicode_literals

import json
import re
import xbmc
import xbmcgui

import connect
import utility


def load():
    if utility.get_setting('selected_profile'):
        connect.load_site_login(utility.profile_switch_url + utility.get_setting('selected_profile'))
#        connect.save_session()
    else:
        utility.log('Load profile: no stored profile found!', loglevel=xbmc.LOGERROR)


def choose():
    profiles = []
    content = utility.decode(connect.load_site_login(utility.profile_url))
    match = json.loads(content)['profiles']
    for item in match:
        profile = {'name': item['firstName'], 'token': item['guid'], 'is_kid': item['experience'] == 'jfk'}
        profiles.append(profile)
    if len(match) > 0:
        dialog = xbmcgui.Dialog()
        nr = dialog.select(utility.get_string(30103), [profile['name'] for profile in profiles])
        if nr >= 0:
            selected_profile = profiles[nr]
        else:
            selected_profile = profiles[0]
        connect.load_site_login(utility.profile_switch_url + selected_profile['token'])
        utility.set_setting('selected_profile', selected_profile['token'])
        utility.set_setting('is_kid', 'true' if selected_profile['is_kid'] else 'false')
        utility.set_setting('profile_name', selected_profile['name'])
#        connect.save_session()
    else:
        utility.log('Choose profile: no profiles were found!', loglevel=xbmc.LOGERROR)


def force_choose():
    utility.set_setting('single_profile', 'false')
    utility.notification(utility.get_string(30304))
    choose()


def update_displayed():
    menu_path = xbmc.getInfoLabel('Container.FolderPath')
    if not utility.get_setting('show_profiles') == 'true':
        utility.set_setting('selected_profile', None)
        connect.save_session()
    xbmc.executebuiltin('Container.Update(' + menu_path + ')')
