#!/usr/bin/env python 


"""
This is the server script that will be started by client over SSH, it takes 
two arguments...
"""

from config import *
from common_tools import *
import socket
import json
import sys
import os.path
import shutil

logger.propagate = False

def main(nonce, filepath, file_hash, file_size, client_path):
  """
  Open a port and wait for connection, write to data to filename.
  """
  sock = get_socket()
  port = sock.getsockname()[1]
  print port

  old_path, history = get_old_filepath(file_hash)
  filepath = validate_filepath(filepath, client_path)
  
  block_count, output_file = get_file_and_state(filepath, old_path)
  print block_count

  partial_file_hash = 0
  if block_count != 0:
    partial_file_hash = getHash(filepath, block_count)

  print partial_file_hash
  
  background()
    
  if file_hash not in history:
    history[file_hash] = {'path' : filepath}

  write_history(history)

  conn, addr = sock.accept()
  logger.info('Connected by %s', addr)

  recvd_nonce = conn.recv(NONCE_SIZE)

  if recvd_nonce != nonce:
    fail("Received nonce %s doesn't match %s.", recvd_nonce, nonce)

  size = recieve_data(conn, output_file, block_count)
  
  if str(size) == file_size:
    logger.info("finished")
    del history[file_hash]

  # Write the new history that does not include this transfer
  write_history(history)

  output_file.close()
  conn.close()

def recieve_data(conn, output_file, block_count):
  """
  Receives data and writes it to disk, stops when it is no longer receiving 
  data.
  """
  output_file.seek(block_count * CHUNK_SIZE)

  size = block_count * CHUNK_SIZE
  while 1:
    data = conn.recv(CHUNK_SIZE)
    output_file.write(data)
    size = size + len(data)
    if len(data) == 0: break

  return size

def background():
  """
  Backgrounds the script.
  """
  logger.info("Entering background.")
  if os.fork():
    sys.exit()

def write_history(history):
  """
  Writes the passed in dictionary to the 
  """
  with open(TRANSACTION_HISTORY_FILENAME, "w") as f:
    json.dump(history, f)
    f.close()

def get_history():
  """
  Looks for the history file and returns a dictionary, empty if not found.
  """
  history = {}
  if os.path.isfile(TRANSACTION_HISTORY_FILENAME):
    history_file = open(TRANSACTION_HISTORY_FILENAME, "r")
    history = json.load(history_file)
    history_file.close()

  return history

def get_file_and_state(filepath, old_path):
  """
  Opens a file object and checks and returns that along with the block count
  on the file.
  """

  block_count = 0
  if old_path:
    block_count = (os.path.getsize(old_path)) / CHUNK_SIZE
    if not os.path.isfile(filepath) or not os.path.samefile(old_path, filepath):
      output_file = open(filepath, "w")
      shutil.copyfile(old_path, filepath)
    else:
      output_file = open(filepath, "r+")
  else:
    output_file = open(filepath, "w")
    block_count = 0

  return block_count, output_file

def validate_filepath(filepath, client_path):
  """
  Validates the filepath, and returns the correct path
  """
  (head, tail) = os.path.split(filepath)
  if not tail:
    if not os.path.exists(head):
      # TODO add error support for warp.py
      fail("Directory " + head + " does not exist.")
    else:
        (client_head, client_tail) = os.path.split(client_path)
        return os.path.join(head, client_tail)

  elif head != "" and not os.path.exists(head):
    fail(filepath + ": No such file or directory")

  elif not head and os.path.isdir(tail):
    (client_head, client_tail) = os.path.split(client_path)
    return os.path.join(tail, client_tail)

  return filepath

def get_old_filepath(file_hash):
  """
  Checks the history file to see if there is a hash of this file in the history
  and then gets that returns that path from the JSON file. If there is no
  record of the file None is returned. 
  """
  old_path = None
  history  = get_history()

  if file_hash in history:
    old_path = history[file_hash]['path']

  return old_path, history

def get_socket():
  """
  Opens and returns a socket on an open port.
  """

  s = None

  try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  except socket.error as msg:
    fail(msg)
  try:
    s.bind(('', 0))
    s.listen(1)
  except socket.error as msg:
    s.close()
    fail(msg)

  return s


if __name__ == '__main__':
  import plac; plac.call(main)
