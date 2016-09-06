#from __future__ import unicode_literals
import os
import sqlite3
import traceback

import sys

try:
    import xbmc
except Exception:
    test = True

from resources.utility import generic_utility

if generic_utility.windows():
    import win32crypt
elif generic_utility.darwin():
    resources_dir = os.path.dirname(os.path.realpath(__file__))
    addon_dir = os.path.join(resources_dir, '..', 'lib')
    sys.path.append(addon_dir)
    import keyring
else:
    from Crypto.Cipher import AES
    from Crypto.Protocol.KDF import PBKDF2

from os.path import expanduser

import datetime
from resources.utility import generic_utility


def to_chrome_date_str(actual):
    delta = actual - datetime.datetime(1601, 1, 1)
    return '%.0f' % (delta.total_seconds()*1000000)

def get_cipher():
    salt = b'saltysalt'
    iv = b' ' * 16
    length = 16

    if generic_utility.darwin():
        my_pass = keyring.get_password('Chrome Safe Storage', 'Chrome')
        iterations = 1003
    else:
        my_pass = 'peanuts'
        iterations = 1

    my_pass = my_pass.encode('utf8')
    key = PBKDF2(my_pass, salt, length, iterations)
    return AES.new(key, AES.MODE_CBC, IV=iv)

def encrypt(str):
    encrypted = None
    if generic_utility.windows():
        encrypted = win32crypt.CryptProtectData(str, None, None, None, None, 0)
    else:
        length = 16 - (len(str) % 16)
        encrypted = 'v10' + get_cipher().encrypt(str+chr(length)*length)
    return encrypted

def has_cookie(conn, name):
    c = conn.cursor()
    c.execute('SELECT count(*) FROM cookies WHERE host_key = ? and name=?',('.netflix.com',name))
    row = c.fetchone()
    count = row[0]
    c.close()
    return count == 1


def update_netflix_id(conn, name, expires_utc, last_access_utc, cookie_data):
    sql = 'UPDATE cookies SET expires_utc=?, last_access_utc=?, encrypted_value=? WHERE host_key = ? and name = ?'
    parms = (expires_utc, last_access_utc, encrypt(cookie_data), '.netflix.com',name)
    cur = conn.cursor()
    cur.execute(sql, parms)
    conn.commit()

def insert_netflix_id(conn, name, expires_utc, last_access_utc, cookie_data, only_secure):
    creation_utc = to_chrome_date_str(datetime.datetime.now())
    sql = 'INSERT INTO cookies values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    sec = 0
    if only_secure == True:
        sec = 1
    parms = (creation_utc, '.netflix.com', name, '', '/', expires_utc, sec, 0, last_access_utc, 1, 1, 1, encrypt(cookie_data), 0)
    cur = conn.cursor()
    cur.execute(sql, parms)
    conn.commit()

def clear_netflix_cookies(conn):
    try:
        sql = 'DELETE FROM cookies where host_key = ?'
        cur = conn.cursor()
        cur.execute(sql, ('.netflix.com',))
        conn.commit()
    except: generic_utility.log('Error clearing Chrome-Cookie: ' +traceback.format_exc(), xbmc.LOGERROR)

def set_cookie(conn, name, value, expires, only_secure = False):
    last_access_utc = to_chrome_date_str(datetime.datetime.now())
    expires_utc = to_chrome_date_str(expires)

    if has_cookie(conn, name):
        update_netflix_id(conn, name, expires_utc, last_access_utc, value)
    else:
        insert_netflix_id(conn, name, expires_utc, last_access_utc, value, only_secure)

def connect():
    db_path = expanduser("~")
    if generic_utility.windows():
        db_path += '\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cookies'
    elif generic_utility.darwin():
        db_path += "/Library/Application Support/Google/Chrome/Default/Cookies"
    else:
        db_path += '/.config/google-chrome/Default/Cookies'
        if not os.path.isfile(db_path):
            db_path = '/storage/.kodi/userdata/addon_data/browser.chromium/profile/Default/Cookies'

    if not os.path.isfile(db_path):
        raise ValueError('Cannot find cookie-file in: '+db_path)

    conn = sqlite3.connect(db_path)
    conn.text_factory = str
    return conn





def set_netflix_cookies(cookies):
    try:
        conn = connect()
        generic_utility.log('cookies: '+str(cookies))
        clear_netflix_cookies(conn)
        for cookie in cookies:
            expires = cookie.expires
            if not expires:
                expires_date = datetime.datetime.now() + datetime.timedelta(days=5)
            else:
                expires_date = datetime.datetime.utcfromtimestamp(expires)
            set_cookie(conn, cookie.name, cookie.value, expires_date)

        conn.commit()
        conn.close()
    except Exception as e:
        generic_utility.log('Error setting Chrome-Cookie: ' +traceback.format_exc(), xbmc.LOGERROR)
