#!/usr/bin/env python


"""
This is the server script that will be started by client over SSH, it takes 
two arguments...
"""

import socket
import json
import sys
import os.path
from config import *

def main(nonce, filepath, hash):
  """
  Open a port and wait for connection, write to data to filename.
  """
  sock = get_socket()
  port = sock.getsockname()[1]

  print port

  # TODO: this only stores one hash in the history file, it should read the old
  # history file then add too it

  # determine the number of block already read by looking in json file
  block_count = 0
  if os.path.isfile(TRANSACTION_HISTORY_FILENAME):
    history_file = open(TRANSACTION_HISTORY_FILENAME, "r")
    history = json.load(history_file)
    if hash in history:
      block_count = history[hash]['block_count']

  print block_count

  conn, addr = sock.accept()
  
  output_file = open(filepath, "r+")
  output_file.seek(block_count * CHUNK_SIZE)

  print 'Connected by', addr
  i = block_count
  while 1:
    data = conn.recv(CHUNK_SIZE)
    output_file.write(data)
    if len(data) != CHUNK_SIZE: break
    else: i = i + 1

  dict = {hash : {"block_count" : i}}
  json.dump(dict, open(TRANSACTION_HISTORY_FILENAME, "w"))

  output_file.close()
  conn.close()

  # TODO: possibly remove the dictionary from the history file once the transfer
  # is successful

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
