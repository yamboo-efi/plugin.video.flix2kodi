import sqlite3
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

from os.path import expanduser

import datetime

from resources import utility


def to_chrome_date_str(actual):
    delta = actual - datetime.datetime(1601, 1, 1)
    return '%.0f' % (delta.total_seconds()*1000000)

def get_cipher():
    salt = b'saltysalt'
    iv = b' ' * 16
    length = 16

    my_pass = 'peanuts'.encode('utf8')

    # 1003 on Mac, 1 on Linux
    iterations = 1

    key = PBKDF2(my_pass, salt, length, iterations)
    return AES.new(key, AES.MODE_CBC, IV=iv)

def encrypt(str):
    length = 16 - (len(str) % 16)
    return get_cipher().encrypt(str+chr(length)*length)

def has_cookie(conn, name):
    c = conn.cursor()
    c.execute('SELECT count(*) FROM cookies WHERE host_key = ? and name=?',('.netflix.com',name))
    row = c.fetchone()
    count = row[0]
    c.close()
    return count == 1


def update_netflix_id(conn, name, expires_utc, last_access_utc, cookie_data):
    sql = 'UPDATE cookies SET expires_utc=?, last_access_utc=?, encrypted_value=? WHERE host_key = ? and name = ?'
    parms = (expires_utc, last_access_utc, 'v10'+encrypt(cookie_data), '.netflix.com',name)
    cur = conn.cursor()
    cur.execute(sql, parms)
    conn.commit()

def insert_netflix_id(conn, name, expires_utc, last_access_utc, cookie_data, only_secure):
    creation_utc = to_chrome_date_str(datetime.datetime.now())
    sql = 'INSERT INTO cookies values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    sec = 0
    if only_secure == True:
        sec = 1
    parms = (creation_utc, '.netflix.com', name, '', '/', expires_utc, sec, 0, last_access_utc, 1, 1, 1, 'v10'+encrypt(cookie_data), 0)
    cur = conn.cursor()
    cur.execute(sql, parms)
    conn.commit()

def set_cookie(conn, name, value, expires, only_secure = False):
    last_access_utc = to_chrome_date_str(datetime.datetime.now())
    expires_utc = to_chrome_date_str(expires)

    if has_cookie(conn, name):
        update_netflix_id(conn, name, expires_utc, last_access_utc, value)
    else:
        insert_netflix_id(conn, name, expires_utc, last_access_utc, value, only_secure)



def set_netflix_cookies(netflix_id, netflix_id_expires, secure_netflix_id, secure_netflix_id_expires):
    conn = sqlite3.connect(expanduser("~")+'/.config/google-chrome/Default/Cookies')
    conn.text_factory = str
    if netflix_id != None:
        set_cookie(conn, 'NetflixId', netflix_id, netflix_id_expires)
    if secure_netflix_id != None:
        set_cookie(conn, 'SecureNetflixId', secure_netflix_id, secure_netflix_id_expires, only_secure=True)

    conn.commit()
    conn.close()
