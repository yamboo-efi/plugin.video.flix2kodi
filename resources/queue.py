from __future__ import unicode_literals

import json
import urllib
import xbmc

import connect
import get
from resources.utility import generic_utility

def add(video_id):
    add_or_remove(video_id, True)

def remove(video_id):
    add_or_remove(video_id, False)

def add_or_remove(video_id, is_add):

    content = connect.load_netflix_site("https://www.netflix.com/")
    falkor_cache = generic_utility.parse_falkorcache(content)

    root_list, my_list = generic_utility.extract_mylist_id(falkor_cache)
    auth = generic_utility.get_setting('authorization_url')

    track_id = get_track_id(my_list)

    if is_add:
        add_or_remove_str = 'addToList'
        add_or_remove_msg = 'added'
    else:
        add_or_remove_str = 'removeFromList'
        add_or_remove_msg = 'removed'

    post = ('{"callPath":["lolomos","%s","%s"],"params":["%s",2,["videos",%s],%s,null,null],'+\
           '"authURL":"%s"}') % (root_list, add_or_remove_str, my_list, video_id, track_id, auth)

    content = connect.load_netflix_site(generic_utility.evaluator()+'&method=call', post, options=True)

    if '"invalidated"' in content:
        generic_utility.notification('Successfully '+add_or_remove_msg)
    elif 'already exists' in content:
        generic_utility.notification('already exists')

    generic_utility.debug('add to mylist content: '+content)


def get_track_id(my_list):
    resp_trackid = get.track_id_list(my_list)
    jsn = json.loads(resp_trackid)
    track_id = jsn['value']['lists'][my_list]['trackIds']['trackId']
    return unicode(track_id)
