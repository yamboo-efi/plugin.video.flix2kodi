from __future__ import unicode_literals

import base64

import list
from resources.utility import generic_utility

language = generic_utility.get_setting('language').split('-')[0]


def netflix(video_type, search_string=None):
    if not search_string:
        search_string = generic_utility.keyboard()
    if search_string:
        list.search(search_string, video_type)
