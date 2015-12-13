from __future__ import unicode_literals

import json
import urllib
import xbmc

import connect
import utility


def add(video_id):
    post_data = utility.my_list % utility.get_setting('authorization_url')
    content = utility.decode(connect.load_netflix_site(utility.evaluator(), post=post_data))
    match = json.loads(content)['value']['videos']
    headers = {'Access-Control-Request-Headers': 'content-type, accept','Access-Control-Request-Method': 'POST',
               'Origin': 'http://www.netflix.com'}
    content = utility.decode(connect.load_netflix_site(utility.evaluator()+'&method=call', options=True, headers=headers))
    print content
    cookies = {'lhpuuidh-browse-' + utility.get_setting('selected_profile'): urllib.quote_plus(utility.get_setting('language').split('-')[1] + ':' + utility.get_setting('language').upper() + ':' + utility.get_setting('root_list')), 'SecureNetflixId': 'v%3D2%26mac%3DAQEAEQABABRkPnYy2LvtMo02JH3beZhI4vKJAM2mLeM.%26dt%3D1449696369549'}
    post_data = utility.add_list % (utility.get_setting('root_list'),
                                    utility.get_setting('my_list'),
                                    video_id,
                                    utility.get_setting('track_id'),
                                    unicode(len(match)),
                                    utility.get_setting('authorization_url'))
    headers = {'Referer': 'http://www.netflix.com/browse',
               'Origin': 'http://www.netflix.com'}
    print post_data
    content = utility.decode(connect.load_netflix_site(utility.evaluator()+'&method=call',
                                               cookies=cookies,
                                               headers=headers,
                                               post=post_data))
    print content
    #xbmc.executebuiltin('XBMC.Notification(NetfliXBMC:,' + str(translation(30144)) + ',3000,' + icon + ')')


def remove(id):
    if authMyList:
        encodedAuth = urllib.urlencode({'authURL': authMyList})
        load(urlMain + "/QueueDelete?" + encodedAuth + "&qtype=ED&movieid=" + id)
        xbmc.executebuiltin('XBMC.Notification(NetfliXBMC:,' + str(translation(30145)) + ',3000,' + icon + ')')
        xbmc.executebuiltin("Container.Refresh")
    else:
        debug("Attempted to removeFromQueue without valid authMyList")
