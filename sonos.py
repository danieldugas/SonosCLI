"""A play local music files example
To use the script:
 * Make sure soco is installed
 * Drop this script into a folder that, besides python files, contains
nothing but music files
 * Adjust the settings on the first three lines of the main function
 * Run the script
"""


from __future__ import print_function, unicode_literals

import os
import time
from random import choice
from subprocess import Popen
try:
    # Python 3
    from urllib.parse import quote
    print('Running as python 3')
except ImportError:
    # Python 2
    from urllib import quote
    print('Running as python 2')

import soco

class SonosInfo(object):
    def __init__(self):
        self.machine_ip = '192.168.0.13'
        self.port = 1337
        self.zone_name = 'Foyer'
        self.directory = '.'
        for zone in soco.discover():
            if zone.player_name == self.zone_name:
                print(self.zone_name)
                self.zone = zone
                break

    def list_files(self):
        music_files = []
        print('Looking for music files')
        for path, dirs, files in os.walk(self.directory):
            for file_ in files:
                if os.path.splitext(file_)[1].startswith('.mp3'):
                    music_files.append(os.path.relpath(os.path.join(path, file_)))
                    print('Found:', music_files[-1])

    def find_file(self, name=None):
        music_files = []
        print('Looking for music files')
        for path, dirs, files in os.walk(self.directory):
            for file_ in files:
                if os.path.splitext(file_)[1].startswith('.mp3'):
                    if name != None:
                        if name in file_:
                            result = os.path.relpath(os.path.join(path, file_))
                    else:
                        music_files.append(os.path.relpath(os.path.join(path, file_)))
                        random_file = choice(music_files)
                        # urlencode all the path parts (but not the /'s)
                        result = os.path.join( *[quote(part) for part in os.path.split(random_file)])
        print('Found: ', result)
        return result

    def play_random_file(self):
        """Add a random non-py file from this folder and subfolders to soco"""
        netpath = 'http://{}:{}/{}'.format(self.machine_ip, self.port, self.find_file())
        print('\nPlaying random file:', netpath)
        self.zone.play_uri(netpath)

    def play_file(self):
        netpath = 'http://{}:{}/{}'.format(self.machine_ip, self.port, self.find_file(name))
        print('\nPlaying file:', netpath)
        self.zone.play_uri(netpath)

    def set_volume(self, vol):
        self.zone.volume = vol

    def stop(self):
        self.zone.stop()





sf = SonosInfo()

log_path = "/tmp/daemon_log.txt"; log = open(log_path, 'wb')
daemon = Popen(["python","daemon.py",str(sf.port)], stdout=log, stderr=log)
time.sleep(0.1)
with open(log_path, 'r') as file_:
    if 'socket.error: [Errno 98] Address already in use\n' in file_.readlines():
        raise ValueError("Server address already in use")


try:
#     sf.play_random_file()
    while True:
       for _ in range(10):
           print("\n")
       keys = raw_input(
       """Welcome to Daniel's SONOS server.
       ------------------------------------
       How may I help you today?

       vol      set volume level
       list     list available music
       play     play a music file
       stop     stop playing audio
       ------------------------------------

       >>""")
       if keys == "vol":
           vol = raw_input("Desired volume level [1-100]: ")
           sf.set_volume(vol)
       if keys == "list":
           sf.list_files()
       if keys == "play":
           sf.play_random_file()
       if keys == "stop":
           sf.stop()
except KeyboardInterrupt:
    print("Exiting.")
except:
    print("Could not read keys")

sf.stop()
daemon.terminate()

