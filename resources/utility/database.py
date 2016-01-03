import os

import sqlite3

import xbmc

def update_playcount(video_id, playcount):
    database_path = get_database_path()

    conn = sqlite3.connect(database_path)
    conn.text_factory = str

    id_file = get_file_id(conn, video_id)
    if id_file:
        c = conn.cursor()
        c.execute('UPDATE files SET playCount=? WHERE idFile = ?', (playcount, id_file))
        c.close()
        conn.commit()

    conn.close()


def get_file_id(conn, video_id):
    c = conn.cursor()
    search_str = '%.V' + video_id + 'V.strm'
    c.execute('SELECT idFile FROM files WHERE files.strFilename like ?', [search_str])
    row = c.fetchone()
    if row:
        id_file = row[0]
    else:
        id_file = None
    c.close()
    return id_file


def get_database_path():
    database_folder = xbmc.translatePath('special://profile/Database')
    dated_files = [(os.path.getmtime(database_folder + os.sep + fn), database_folder + os.sep + fn)
                   for fn in os.listdir(database_folder) if
                   fn.lower().startswith('myvideos') and fn.lower().endswith('.db')]
    dated_files.sort()
    dated_files.reverse()
    database_path = dated_files[0][1]
    return database_path