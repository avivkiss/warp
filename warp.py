#!/usr/bin/env python

"""
This is the main driver script that will run on the client.
"""

from config import *
from common_tools import *
import random, os.path
from handshake import handshake
from clint.textui import progress
import plac
import socket
import time

@plac.annotations(
    tcp_mode=('TCP mode', 'flag', 't'),
    recursive = ('prints', 'flag', 'r'),
    disable_verify = ('Disable verify', 'flag', 'v'))
def main(remote_host, recursive, file_src, file_dest, tcp_mode, disable_verify):
  (head, tail) = os.path.split(file_src)

  global TCP_MODE
  TCP_MODE = tcp_mode

  logger.info("Using TCP: " + str(TCP_MODE))

  if os.path.isdir(file_src) and not recursive:
    logger.error("%s is a directory", file_src)
    return
  elif not tail and os.path.isfile(head):
    logger.error("%s: not a directory", file_src)
    return
  elif not os.path.isdir(file_src) and \
    not os.path.isfile(file_src):
      logger.error("%s no such file or directory", file_src)
      return
  username, hostname, ssh_port = unpack_remote_host(remote_host)
  nonce = generate_nonce()
  file_hash = getHash(file_src)
  # handshake should be returning a tuple, port and numblocks TODO
  sock, block_count, server, thread, client = handshake(username=username, hostname=hostname, \
    nonce=nonce, file_dest=file_dest, file_hash=file_hash, \
    file_size=os.path.getsize(file_src), file_src=file_src, tcp_mode=tcp_mode, \
    disable_verify=disable_verify)

  send_data(sock, file_src, block_count)

  if(thread.is_alive()):
    print "alive"
  else:
    print "not alive"

  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect(('localhost', CONTROL_PORT))
  s.send('Hello, world')
  data = s.recv(1024)
  s.close()
  print "sent"
  print "got ", data
  server.shutdown()
  server.socket.close()

def send_data(sock, file_src, block_count = 0):
  """
  Opens the file at the number of blocks passed in and uses that along with
  the other parameters to send a file to the host at the specified port.
  """
  f = open(file_src, 'r')
  f.seek(block_count * CHUNK_SIZE)
  data = f.read(CHUNK_SIZE)
  with progress.Bar(label="", expected_size=os.path.getsize(file_src)) as bar:
    while data :
      bar.show(f.tell())
      # TODO make this same array every time
      if not TCP_MODE:
        sendChunk(sock, bytearray(data))
      else:
        sock.sendall(data)
      data = f.read(CHUNK_SIZE)
  logger.info("Data sent.")
  sock.close()

def sendChunk(sock, data):
  size = sock.send(data)
  if not size == len(data):
    sendChunk(sock, data[size:])

def generate_nonce(length=NONCE_SIZE):
  """Generate pseudorandom number. Ripped from google."""
  return ''.join([str(random.randint(0, 9)) for i in range(length)])


def unpack_remote_host(remote_host):
  """
  Parses the hostname and breaks it into host and user. Modified from paramiko
  """
  username = ''
  hostname = ''
  port = 22

  if remote_host.find('@') >= 0:
    username, hostname = remote_host.split('@')

  if len(hostname) == 0 or len(username) == 0:
    fail('Hostname/username required.')

  if hostname.find(':') >= 0:
    hostname, portstr = hostname.split(':')
    port = int(portstr)

  return (username, hostname, port)

if __name__ == '__main__':
  plac.call(main)
