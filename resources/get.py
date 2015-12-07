from __future__ import unicode_literals

import time
import xbmc
import xbmcvfs

import connect
import search
import utility


def video_info(video_id):
    content = ''
    cache_file = xbmc.translatePath(utility.cache_dir() + video_id + '.cache')
    if xbmcvfs.exists(cache_file):
        file_handler = xbmcvfs.File(cache_file, 'rb')
        content = file_handler.read()
        file_handler.close()
    if not content:
        post_data = utility.video_info % (video_id, video_id, video_id, video_id,
                                         utility.get_setting('authorization_url'))
        content = connect.load_site(utility.evaluator(), post=post_data)
        file_handler = xbmcvfs.File(cache_file, 'wb')
        file_handler.write(content)
        file_handler.close()
    return utility.decode(content)


def series_info(series_id):
    content = ''
    cache_file = xbmc.translatePath(utility.cache_dir() + series_id + '_episodes.cache')
    if xbmcvfs.exists(cache_file) and (time.time() - xbmcvfs.Stat(cache_file).st_mtime() < 60 * 5):
        file_handler = xbmcvfs.File(cache_file, 'rb')
        content = file_handler.read()
        file_handler.close()
    if not content:
        url = utility.series_url % (utility.get_setting('api_url'), series_id)
        content = connect.load_site(url)
        file_handler = xbmcvfs.File(cache_file, 'wb')
        file_handler.write(content)
        file_handler.close()
    return utility.decode(content)


def cover(video_type, video_id, title, year):
    filename = video_id + '.jpg'
    filename_none = video_id + '.none'
    cover_file = xbmc.translatePath(utility.cover_cache_dir() + filename)
    cover_file_none = xbmc.translatePath(utility.cover_cache_dir() + filename_none)
    fanart_file = xbmc.translatePath(utility.fanart_cache_dir() + filename)
    content = search.tmdb(video_type, title, year)
    if content['total_results'] > 0:
        content = content['results'][0]
        try:
            cover_url = utility.picture_url + content['poster_path']
            content_jpg = connect.load_site(cover_url)
            file_handler = open(cover_file, 'wb')
            file_handler.write(content_jpg)
            file_handler.close()
        except Exception:
            file_handler = open(cover_file_none, 'wb')
            file_handler.write('')
            file_handler.close()
            pass
        try:
            fanart_url = utility.picture_url + content['backdrop_path']
            content_jpg = connect.load_site(fanart_url)
            file_handler = open(fanart_file, 'wb')
            file_handler.write(content_jpg)
            file_handler.close()
        except Exception:
            pass


def trailer(video_type, title):
    content = search.tmdb(video_type, title)
    if content['total_results'] > 0:
        content = content['results'][0]
        tmdb_id = content['id']
        content = search.trailer(video_type, tmdb_id)
    else:
        utility.notification(utility.get_string(30305))
        content = None
    return content
