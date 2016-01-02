from __future__ import unicode_literals

import json
import xbmc
import xbmcgui

import connect
from resources.utility import generic_utility


def load():
    profile_id = generic_utility.get_setting('selected_profile')
    if profile_id:
        switch_profile(profile_id)
    else:
        generic_utility.log('Load profile: no stored profile found!', loglevel=xbmc.LOGERROR)


def switch_profile(profile_id):
    auth_id = generic_utility.get_setting('authorization_url')
    profile_switch_url = generic_utility.profile_switch() + 'switchProfileGuid=' + profile_id + '&authURL=' + auth_id
    ret = connect.load_netflix_site(profile_switch_url)
#    generic_utility.log('switch-profile: '+ret)
    connect.set_chrome_netflix_cookies()

def choose():
    profiles = []
    content = connect.load_netflix_site(generic_utility.profile_url)
    match = json.loads(content)['profiles']
    for item in match:
        profile = {'name': item['firstName'], 'token': item['guid'], 'is_kid': item['experience'] == 'jfk'}
        profiles.append(profile)
    if len(match) > 0:
        dialog = xbmcgui.Dialog()
        nr = dialog.select(generic_utility.get_string(30103), [profile['name'] for profile in profiles])
        if nr >= 0:
            selected_profile = profiles[nr]
        else:
            selected_profile = profiles[0]

        switch_profile(selected_profile['token'])

        generic_utility.set_setting('selected_profile', selected_profile['token'])
        generic_utility.set_setting('is_kid', 'true' if selected_profile['is_kid'] else 'false')
        generic_utility.set_setting('profile_name', selected_profile['name'])
    else:
        generic_utility.log('Choose profile: no profiles were found!', loglevel=xbmc.LOGERROR)


def force_choose():
    generic_utility.set_setting('single_profile', 'false')
    generic_utility.notification(generic_utility.get_string(30304))
    choose()


def update_displayed():
    menu_path = xbmc.getInfoLabel('Container.FolderPath')
    if not generic_utility.get_setting('show_profiles') == 'true':
        generic_utility.set_setting('selected_profile', None)
    xbmc.executebuiltin('Container.Update(' + menu_path + ')')
