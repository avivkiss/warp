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
from udt4py import UDTSocket
import plac

logger.propagate = False

@plac.annotations(tcp_mode=('TCP mode', 'flag', 't'),
                  disable_verify=('Disable verify', 'flag', 'v'))
def main(nonce, filepath, file_hash, file_size, client_path, tcp_mode, disable_verify):
  """
  Open a port and wait for connection, write to data to filename.
  """

  global TCP_MODE 
  TCP_MODE = tcp_mode
  logger.info("Using TCP: " + str(TCP_MODE))

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
  
  if not TCP_MODE:
    udt_sock = UDTSocket()
    udt_sock.bind(sock.fileno())
    udt_sock.listen()
    conn, addr = udt_sock.accept()
    logger.info('Connected by %s', addr)

    recvd_nonce = bytearray(NONCE_SIZE) 
    conn.recv(recvd_nonce)
    recvd_nonce = str(recvd_nonce)
  else: 
    conn, addr = sock.accept()
    logger.info('Connected by %s', addr)

    recvd_nonce = conn.recv(NONCE_SIZE)

  if recvd_nonce != nonce:
    fail("Received nonce %s doesn't match %s.", recvd_nonce, nonce)

  size = recieve_data(conn, output_file, block_count, file_size)
  
  output_file.close()
  if str(size) == file_size:
    logger.info("finished")
    del history[file_hash]
    if not disable_verify:
        if not file_hash == getHash(filepath):
          logger.info("error: files do not match")
        else:
          logger.info("files match")

  # Write the new history that does not include this transfer
  write_history(history)
  conn.close()

  if not TCP_MODE:
    udt_sock.close()

  sock.close()

  os._exit(0)

def recieve_data(conn, output_file, block_count, file_size):
  """
  Receives data and writes it to disk, stops when it is no longer receiving 
  data.
  """
  output_file.seek(block_count * CHUNK_SIZE)

  size = block_count * CHUNK_SIZE
  data = bytearray(CHUNK_SIZE)

  if not TCP_MODE:
    while 1:
      len_rec = conn.recv(data)
      data = str(data)
      output_file.write(data[:len_rec])
      size = size + len_rec

      if len_rec == 0 or str(size) == str(file_size): break
  else:
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
    sock.close()
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

  if TCP_MODE:
    sock_type = socket.SOCK_STREAM
  else:
    sock_type = socket.SOCK_DGRAM

  try:
    s = socket.socket(socket.AF_INET, sock_type)
  except socket.error as msg:
    fail(msg)
  try:
    s.bind(('', 0))
    if TCP_MODE:
      s.listen(1)
  except socket.error as msg:
    s.close()
    fail(str(msg))

  return s


if __name__ == '__main__':
  plac.call(main)
