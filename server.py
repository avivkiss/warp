#!/usr/bin/env python


"""
This is the server script that will be started by client over SSH, it takes 
two arguments...
"""

from config import *
import socket
import json
import sys
import os.path
import shutil

def main(nonce, filepath, hash, file_size):
  """
  Open a port and wait for connection, write to data to filename.
  """
  sock = get_socket()
  port = sock.getsockname()[1]

  print port

  history = {}

  # determine the number of block already read by looking in json file
  block_count = 0
  old_path = ""
  if os.path.isfile(TRANSACTION_HISTORY_FILENAME):
    history_file = open(TRANSACTION_HISTORY_FILENAME, "r")
    history = json.load(history_file)
    history_file.close()
    if hash in history:
      old_path = history[hash]['path']

  (head, tail) = os.path.split(filepath)
  if not tail:
    # putting this through the logger because at this point the server
    # is headless and the user will not see the message, TODO add support for
    # this message in warp.py
    logger.error("must specify a valid file path")
    sys.exit()

  if head != "" and not os.path.exists(head):
      os.makedirs(head)

  if old_path != "":
    block_count = (os.path.getsize(old_path)) / CHUNK_SIZE
    if not os.path.isfile(filepath) or not os.path.samefile(old_path, filepath):
      output_file = open(filepath, "w")
      shutil.copyfile(old_path, filepath)
    else:
      output_file = open(filepath, "r+")
  else:
    output_file = open(filepath, "w")
    block_count = 0

  print block_count

  # background self
  logging.info("About to background:")
  if os.fork():
    logging.info("Backgrounded:")
    sys.exit()
    
  logging.info("Resuming:")
  if hash not in history:
    history[hash] = {'path' : filepath}

  # At this point we have created the new file so the transaction
  # history should be updated
  with open(TRANSACTION_HISTORY_FILENAME, "w") as f:
    json.dump(history, f)
    f.close()

  conn, addr = sock.accept()
  
  output_file.seek(block_count * CHUNK_SIZE)

  logger.info('Connected by %s', addr)
  i = block_count
  size = block_count * CHUNK_SIZE
  while 1:
    data = conn.recv(CHUNK_SIZE)
    output_file.write(data)
    size = size + len(data)
    if len(data) != CHUNK_SIZE: break
    else: i = i + 1

  if str(size) == file_size:
    logger.info("finished")
    del history[hash]

  # Write the new history that does not include this transfer
  with open(TRANSACTION_HISTORY_FILENAME, "w") as f:
    json.dump(history, f)
    f.close()

  output_file.close()
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
