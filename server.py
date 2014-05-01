#!/usr/bin/env python


"""
This is the server script that will be started by client over SSH, it takes 
two arguments...
"""

import socket
import json
import sys
from config import *

def main(nonce, filename, hash):
  """
  Open a port and wait for connection, write to data to filename.
  """
  sock = get_socket()
  port = sock.getsockname()[1]

  print port

  conn, addr = sock.accept()
  
  ouput_file = open(filename, 'w')

  print 'Connected by', addr
  while 1:
    data = conn.recv(CHUNK_SIZE)
    ouput_file.write(data)
    if not data: break

  ouput_file.close()
  conn.close()

def get_socket():
  """
  Opens and returns a socket on an open port.
  """

  s = None

  try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  except socket.error as msg:
    print msg
    sock_fail()
  try:
    s.bind(('', 0))
    s.listen(1)
  except socket.error as msg:
    s.close()
    print msg
    sock_fail()

  return s

def sock_fail():
  print 'could not open socket'
  sys.exit(1)

if __name__ == '__main__':
  import plac; plac.call(main)
