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
import urllib
from random import choice
from subprocess import Popen, call
from multiprocessing import Process
from threading import Thread
try:
    # Python 3
    from urllib.parse import quote
    print('Running as python 3')
except ImportError:
    # Python 2
    from urllib import quote
    print('Running as python 2')

import soco

MY_IP = raw_input("What's my IP address?\n>>")
if MY_IP == '': MY_IP = '172.22.22.57'

class SonosInfo(object):
    def __init__(self,ip):
        self.machine_ip = ip
        self.port = 1337
        self.zone_name = 'Foyer'
        self.directory = '.'
        self.streaming = False
        for zone in soco.discover():
            self.zone = zone
            if zone.player_name == self.zone_name:
                break
        self.zone_name = self.zone.player_name
        print(self.zone_name)

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
        except Exception as exc:
          print("Could not play song.")
          print(exc)
        # Append original queue
        for item in queue[1:]:
            self.zone.add_to_queue(item)

    def queue(self, keyword=None):
        if keyword != None:
            # Add current uris to queue
            tracks = self.list_files(keyword)['paths']
            for path in tracks:
                quote_path = urllib.quote(path)
                netpath = 'http://{}:{}/{}'.format(self.machine_ip, self.port, quote_path)
                print(netpath)
                self.zone.add_uri_to_queue(netpath)
            print("Added", len(tracks), "tracks to the queue.")
        for i, item in enumerate(self.zone.get_queue()[1:]):
            if i == 0: print("Next up:")
            print("  ", item.title)


    def clear(self, keyword=None):
        self.zone.clear_queue()

    def resume(self):
        self.zone.play()

    def pause(self):
        self.zone.pause()

    def set_volume(self, vol):
        self.zone.volume = vol
        print("Volume set to", vol)

    def stop(self):
        self.zone.stop()
        self.streaming = False

    def stream(self, stream_path="darkice.mp3"):
        netpath = 'http://{}:{}/{}'.format(self.machine_ip, self.port, stream_path)
        self.zone.play_uri(netpath)
        print(netpath)
        self.streaming = True





sf = SonosInfo(MY_IP)

log_path = "/tmp/daemon_log.txt"; log = open(log_path, 'wb')
daemon = Popen(["python","daemon.py",str(sf.port)], stdout=log, stderr=log)
time.sleep(0.1)
with open(log_path, 'r') as file_:
    if 'socket.error: [Errno 98] Address already in use\n' in file_.readlines():
        raise ValueError("Server address already in use")


def show_status(sf):
    global FLAGS
    while True:
        break
        try:
            track_info = sf.zone.get_current_track_info()
            transport_info = sf.zone.get_current_transport_info()
            queue = sf.zone.get_queue()
            try:
                sf.resume()
            except:
                print("", end='')
        except KeyboardInterrupt:
            break
#         except Exception as exp:
#             raise exp
#             print(exp)
#             print("")

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
        denom = "stream" if sf.streaming else "track"
        print("Current",denom,"[" + transport_info['current_transport_state'] + "]:",
              track_info['title'], "      ", track_info['position'], "/", track_info['duration'])
        print("")
        for item in queue[1:2]:
            print("Next up:")
            print("  ", item.title)

        print(FLAGS)
        print(">>", end='')

        try:
            time.sleep(0.1)
            while True:
                if FLAGS['pause']:
                    time.sleep(1)
                else:
                    break
                if FLAGS['wait']:
                    time.sleep(5)
                    FLAGS['wait'] = False
                    break
                if FLAGS['end']:
                    raise KeyboardInterrupt
        except KeyboardInterrupt:
            break

def pause_status_until_enter():
    global FLAGS
    FLAGS['pause'] = True
    raw_input("...")
    FLAGS['pause'] = False

try:
    global FLAGS
    FLAGS = {'pause': False, 'wait': False, 'end': False}
    p = Thread(target=show_status, args=(sf,))
    p.start()
#     sf.play_random_file()
    while True:
       keys = raw_input(" >>")
       cmd = keys.split(' ', 1) + [None]
       if cmd[0] == "vol":
           print("Current volume:", sf.zone.volume)
           vol = raw_input("Desired volume level [1-100]: ")
           sf.set_volume(vol)
       elif cmd[0] == "list":
           sf.list(cmd[1])
           pause_status_until_enter()
       elif cmd[0] == "play":
           sf.play(cmd[1])
       elif cmd[0] == "stop":
           sf.stop()
       elif cmd[0] == "queue":
           sf.queue(cmd[1])
           pause_status_until_enter()
       elif cmd[0] == "clear":
           sf.clear()
       elif cmd[0] == "resume":
           sf.resume()
       elif cmd[0] == "pause":
           sf.pause()
       elif cmd[0] == "stream":
           sf.stream()
       else:
           print("Unknown command: '"+ keys+ "'.")
except KeyboardInterrupt:
    print("Exiting.")
    FLAGS['end'] = True
finally:
    #sf.stop()
    daemon.terminate()
    p.join()
