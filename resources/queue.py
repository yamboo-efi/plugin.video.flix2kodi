from __future__ import unicode_literals

import json
import re
import urllib
import xbmc

import connect
import get
from resources.path_evaluator.types.lolomos import get_root_list, get_mylist
from resources.utility import generic_utility
from resources.utility.generic_utility import get_string


def add(video_id):
    add_or_remove(video_id, True)


def remove(video_id):
    add_or_remove(video_id, False)
    xbmc.executebuiltin("Container.Refresh")


def add_or_remove(video_id, is_add):
    root_list = get_root_list()

    my_list = get_mylist(root_list)[0]
    auth = generic_utility.get_setting('authorization_url')
    track_id = get.track_id_list(my_list)

    if is_add:
        add_or_remove_str = 'addToList'
        add_or_remove_msg = 'added'
    else:
        add_or_remove_str = 'removeFromList'
        add_or_remove_msg = 'removed'

    post = ('{"callPath":["lolomos","%s","%s"],"params":["%s",2,["videos",%s],%s,null,null],' +
            '"authURL":"%s"}') % (root_list, add_or_remove_str, my_list, video_id, track_id, auth)

    content = connect.load_netflix_site(generic_utility.evaluator()+'&method=call', post, options=True)

    jsn = json.loads(content)

    generic_utility.log('mylist: '+my_list)
    generic_utility.log(str(jsn))
    if '"invalidated"' in content:
        generic_utility.notification('Successfully '+add_or_remove_msg)
    elif 'already exists' in content:
        generic_utility.notification('already exists')

    generic_utility.debug('add to mylist content: '+content)
