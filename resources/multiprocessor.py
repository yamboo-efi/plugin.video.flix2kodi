import thread
import threading
import time
import traceback

import requests

from resources import utility
from resources.video_parser import video

def load_data(matches, video_type, run_as_widget, loading_progress, url = '', viewing_activity=False):
    video_add_args = []

    lock = thread.allocate_lock()
    max_threads = 4
    threads = [None] * max_threads
    rets = [None] * max_threads
    size = 0
    thread_id = 0
    for match in matches:
        if (thread_id == max_threads):
            #            utility.log('max reached, waiting for join')
            for thread_id in range(len(threads)):
                threads[thread_id].join()
                video_add_args.append(rets[thread_id])
                threads[thread_id] = None
                rets[thread_id] = None
            #            utility.log('all joined')
            thread_id = 0

        #        utility.log(video_id)
        if viewing_activity == True:
            threads[thread_id] = threading.Thread(target=view_activity_load_match, args=(match, video_type, lock, rets, thread_id))
        else:
            threads[thread_id] = threading.Thread(target=video_load_match, args=(match, video_type, url, lock, rets, thread_id))

        threads[thread_id].start()
        #        utility.log('thread '+str(i)+' started')
        size += 1
        if not run_as_widget:
            utility.progress_window(loading_progress, size * 100 / len(matches), 'processing...')

        thread_id += 1

    for thread_id in range(len(threads)):
        if threads[thread_id] != None:
            threads[thread_id].join()
            video_add_args.append(rets[thread_id])
            threads[thread_id] = None
            rets[thread_id] = None
            #    utility.log('all joined')
    return video_add_args


def video_load_match(video_id, video_type, url, lock, rets, thread_id):
    load_match_internal(thread_id, lock, rets, video_id, video_type, url=url)


def view_activity_load_match(item, video_type, lock, rets, thread_id):
    series_id = 0
    is_episode = False
    video_id = unicode(item['movieID'])
    date = item['dateStr']
    try:
        series_id = item['series']
        series_title = item['seriesTitle']
        title = item['title']
        title = series_title + ' ' + title
    except Exception:
        title = item['title']
    title = date + ' - ' + title
    if series_id > 0:
        is_episode = True

    load_match_internal(thread_id, lock, rets, video_id, video_type, title=title, is_episode=is_episode)


def load_match_internal(thread_id, lock, rets, video_id, video_type, title='', url='', is_episode =False):
    #    utility.log('loading '+unicode(video_id))
    ret = None
    success = False
    while (success == False):
        try:
            ret = video(video_id, title, '', is_episode, False, video_type, url, lock)
            success = True
        except requests.exceptions.HTTPError, e:
            if e.response.status_code == 429:
                time.sleep(2)
            else:
                utility.log('error loading video ' + unicode(video_id) + '\n' + traceback.format_exc(), xbmc.LOGERROR)
                break
        except Exception as e:
            utility.log('error loading video ' + unicode(video_id) + '\n' + traceback.format_exc(), xbmc.LOGERROR)
            break
        #    utility.log('finished '+video_id)
    rets[thread_id] = ret


