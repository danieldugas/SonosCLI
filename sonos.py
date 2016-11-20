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

    def list_files(self, keyword=None, verbose=False):
        # Populate list
        music_files = []
        for path, dirs, files in os.walk(self.directory):
                for file_ in files:
                    if os.path.splitext(file_)[1].startswith('.mp3'):
                        music_files.append(os.path.relpath(os.path.join(path, file_)))
        ids = list(range(len(music_files)))
        # Filter list
        if keyword != None:
            if keyword.isdigit():
                music_files = [music_files[ids.index(int(keyword))]]
                ids = [ids[ids.index(int(keyword))]]
            else:
                ids_filtered = [id_ for id_, file_ in zip(ids, music_files) 
                                if keyword in file_]
                music_files_filtered = [file_ for id_, file_ in zip(ids, music_files) 
                                        if keyword in file_]
                ids = ids_filtered
                music_files = music_files_filtered
        # Print list
        if verbose:
            for id_, music_file in zip(ids, music_files):
                print(id_, ') ', music_file)
            if len(ids) == 0: print("File containing", keyword, "not found")
        return {'ids': ids, 'paths': music_files}

    def list(self, keyword=None):
        self.list_files(keyword=keyword, verbose=True)

    def play(self, keyword=None):
        if keyword == None:
            import random
            keyword = str(random.choice(self.list_files(verbose=False)['ids']))
        # Clear queue but save it for later
        queue = self.zone.get_queue()
        self.zone.clear_queue()
        # Add current uris to queue
        self.queue(keyword)
        try:
          self.zone.play_from_queue(0)
        except:
          print("Could not play song.")
        # Append original queue
        for item in queue[1:]:
            self.zone.add_to_queue(item)
        time.sleep(0.1)

    def queue(self, keyword=None):
        if keyword != None:
            # Add current uris to queue
            formatted = [os.path.join( *[quote(part) for part in os.path.split(file_)])
                         for file_ in self.list_files(keyword)['paths']]
            for path in formatted:
                netpath = 'http://{}:{}/{}'.format(self.machine_ip, self.port, path)
                self.zone.add_uri_to_queue(netpath)
            print("Added", len(formatted), "tracks to the queue.")
        for i, item in enumerate(self.zone.get_queue()[1:]):
            if i == 0: print("Next up:")
            print("  ", item.title)


    def clear(self, keyword=None):
        self.zone.clear_queue()

    def resume(self):
        self.zone.play()
        time.sleep(0.1)

    def pause(self):
        self.zone.pause()
        time.sleep(0.1)

    def set_volume(self, vol):
        self.zone.volume = vol
        print("Volume set to", vol)

    def stop(self):
        self.zone.stop()
        time.sleep(0.1)





sf = SonosInfo()

log_path = "/tmp/daemon_log.txt"; log = open(log_path, 'wb')
daemon = Popen(["python","daemon.py",str(sf.port)], stdout=log, stderr=log)
time.sleep(0.1)
with open(log_path, 'r') as file_:
    if 'socket.error: [Errno 98] Address already in use\n' in file_.readlines():
        raise ValueError("Server address already in use")


def show_status():
   for _ in range(10):
       print("\n")
   print("""
Welcome to Daniel's SONOS server.
------------------------------------
How may I help you today?

vol      set volume level
list     list available music
play     play a music file
stop     stop playing audio
queue    add music to queue
clear    clear queue
resume   resume track
pause    pause track
------------------------------------
""")
   try:
       track_info = sf.zone.get_current_track_info()
       print("Current track [" + sf.zone.get_current_transport_info()['current_transport_state'] + "]:",
             track_info['title'])
       print("")
       for item in sf.zone.get_queue()[1:2]:
           print("Next up:")
           print("  ", item.title)
   except:
       print("")

try:
#     sf.play_random_file()
    show_status()
    while True:
       keys = raw_input(" >>")
       show_status()
       cmd = keys.split(' ', 1) + [None]
       if cmd[0] == "vol":
           print("Current volume:", sf.zone.volume)
           vol = raw_input("Desired volume level [1-100]: ")
           sf.set_volume(vol)
       elif cmd[0] == "list":
           sf.list(cmd[1])
       elif cmd[0] == "play":
           sf.play(cmd[1])
       elif cmd[0] == "stop":
           sf.stop()
           show_status()
       elif cmd[0] == "queue":
           sf.queue(cmd[1])
       elif cmd[0] == "clear":
           sf.clear()
       elif cmd[0] == "resume":
           sf.resume()
           show_status()
       elif cmd[0] == "pause":
           sf.pause()
           show_status()
       else:
           print("Unknown command: '"+ keys+ "'.")
except KeyboardInterrupt:
    print("Exiting.")
except:
    raise
finally:
    sf.stop()
    daemon.terminate()

sf.stop()
daemon.terminate()

