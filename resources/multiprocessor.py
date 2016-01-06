from __future__ import unicode_literals

import requests
import thread
import threading
import time
import traceback
import xbmc

from resources.utility import generic_utility
from resources.video_parser import video


def load_data(metadatas, video_type, run_as_widget, loading_progress, viewing_activity = False):
    video_add_args = []

    lock = thread.allocate_lock()
    max_threads = 4
    threads = [None] * max_threads
    rets = [None] * max_threads
    size = 0
    thread_id = 0
    for metadata in metadatas:
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

        threads[thread_id] = threading.Thread(target=load_match, args=(thread_id, lock, rets, metadata, viewing_activity))

        threads[thread_id].start()
        #        utility.log('thread '+str(i)+' started')
        size += 1
        if not run_as_widget:
            generic_utility.progress_window(loading_progress, size * 100 / len(metadata), 'processing...')

        thread_id += 1

    for thread_id in range(len(threads)):
        if threads[thread_id] != None:
            threads[thread_id].join()
            video_add_args.append(rets[thread_id])
            threads[thread_id] = None
            rets[thread_id] = None
            #    utility.log('all joined')
    return video_add_args


def load_match(thread_id, lock, rets, metadata, viewing_activity = False):
#    utility.log('loading '+unicode(video_id))
    ret = None

    custom_title = None
    series_title = None
    if viewing_activity==True:
        video_id = metadata['id']
        custom_title = metadata['title']
        series_title = metadata['series_title']
    else:
        video_id = metadata
    success = False
    while (success == False):
        try:
            ret = video(video_id, lock, custom_title = custom_title, series_title = series_title)
            success = True
        except requests.exceptions.HTTPError, e:
            if e.response.status_code == 429:
                time.sleep(2)
            else:
                generic_utility.log('error loading video ' + unicode(video_id) + '\n' + traceback.format_exc(), xbmc.LOGERROR)
                break
        except Exception as e:
            generic_utility.log('error loading video ' + unicode(video_id) + '\n' + traceback.format_exc(), xbmc.LOGERROR)
            break
        #    utility.log('finished '+video_id)
    rets[thread_id] = ret


