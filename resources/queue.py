from __future__ import unicode_literals

import json
import urllib
import xbmc

import connect
from resources.utility import generic_utility

my_list = '{"paths":[["lolomo",{"from":2,"to":2},{"from":0,"to":50},["summary","title"]],' \
          '["lolomo",{"from":1,"to":2},["trackIds","displayName"]]],"authURL":"%s"}'

def add(video_id):
    post_data = my_list % generic_utility.get_setting('authorization_url')
    content = connect.load_netflix_site(generic_utility.evaluator(), post=post_data)
    match = json.loads(content)['value']['videos']
    headers = {'Access-Control-Request-Headers': 'content-type, accept','Access-Control-Request-Method': 'POST',
               'Origin': 'http://www.netflix.com'}
    connect.load_netflix_site(generic_utility.evaluator() + '&method=call', options=True, headers=headers)
    cookies = {'lhpuuidh-browse-' + generic_utility.get_setting('selected_profile'): urllib.quote_plus(
        generic_utility.get_setting('language').split('-')[1] + ':' + generic_utility.get_setting('language').upper() + ':' + generic_utility.get_setting('root_list')), 'SecureNetflixId': 'v%3D2%26mac%3DAQEAEQABABRkPnYy2LvtMo02JH3beZhI4vKJAM2mLeM.%26dt%3D1449696369549'}
    post_data = generic_utility.add_list % (generic_utility.get_setting('root_list'),
                                            generic_utility.get_setting('my_list'),
                                            video_id,
                                            generic_utility.get_setting('track_id'),
                                            unicode(len(match)),
                                            generic_utility.get_setting('authorization_url'))
    headers = {'Referer': 'http://www.netflix.com/browse',
               'Origin': 'http://www.netflix.com'}
    content = connect.load_netflix_site(generic_utility.evaluator() + '&method=call',
                                        cookies=cookies,
                                        headers=headers,
                                        post=post_data)
    #xbmc.executebuiltin('XBMC.Notification(NetfliXBMC:,' + str(translation(30144)) + ',3000,' + icon + ')')


def remove(id):
    if authMyList:
        encodedAuth = urllib.urlencode({'authURL': authMyList})
        load(urlMain + "/QueueDelete?" + encodedAuth + "&qtype=ED&movieid=" + id)
        xbmc.executebuiltin('XBMC.Notification(NetfliXBMC:,' + str(translation(30145)) + ',3000,' + icon + ')')
        xbmc.executebuiltin("Container.Refresh")
    else:
        debug("Attempted to removeFromQueue without valid authMyList")
