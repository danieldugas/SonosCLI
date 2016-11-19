from __future__ import print_function, unicode_literals

import os
import time
from threading import Thread
from random import choice
try:
    # Python 3
    from urllib.parse import quote
    from http.server import SimpleHTTPRequestHandler
    from socketserver import TCPServer
    import socket 
    print('Running as python 3')
except ImportError:
    # Python 2
    from urllib import quote
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from SocketServer import TCPServer
    import socket
    print('Running as python 2')


import sys
argv = sys.argv
try:
  port = int(argv[1])
except:
  print("Usage: python daemon.py [port_number]")
handler = SimpleHTTPRequestHandler
tcpserver = TCPServer(("", port), handler)
tcpserver.serve_forever()

tcpserver.socket.close()
